# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2020 Matthias Lohr <mail@mlohr.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from web3 import Web3
from web3.datastructures import AttributeDict
from web3.exceptions import TimeExhausted
from web3.gas_strategies.time_based import fast_gas_price_strategy
from web3.providers.base import BaseProvider
from web3.types import TxParams, Wei

from bdtsim.account import Account
from bdtsim.account_related_diff_collection import FundsDiffCollection, ItemShareCollection
from bdtsim.contract import Contract
from bdtsim.simulation_result import TransactionLogEntry


logger = logging.getLogger(__name__)


class Environment(object):
    def __init__(self, web3_provider: BaseProvider, operator: Account, seller: Account, buyer: Account,
                 chain_id: Optional[int] = None, gas_price: Optional[int] = None,
                 gas_price_strategy: Optional[Callable[[Web3, Optional[TxParams]], Wei]] = None,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize Environment

        Args:
            web3_provider (BaseProvider:
            operator (Account):
            seller (Account):
            buyer (Buyer):
            chain_id (Optional[int]):
            gas_price (Optional[int]):
            gas_price_strategy (Optional[Callable[[Web3, Optional[TxParams]], Wei]]):
            *args (Any): Collector for unrecognized positional arguments
            **kwargs (Any): Collector for unrecognized keyword arguments
        """

        if len(args):
            raise TypeError('Unrecognized positional argument "%s" for Environment' % str(args[0]))
        if len(kwargs):
            raise TypeError('Unrecognized keyword argument "%s" for Environment' % str(list(kwargs.keys())[0]))

        self._web3 = Web3(web3_provider)

        self._operator = operator
        self._seller = seller
        self._buyer = buyer

        if chain_id is None:
            self._chain_id = self._web3.eth.chainId
            if self._chain_id is not None:
                logger.debug('Auto-detected chain id %d' % self._chain_id)
            else:
                logger.warning('Failed auto-detecting chain id')
        else:
            self._chain_id = chain_id

        self._gas_price = gas_price
        if gas_price_strategy is not None:
            self._web3.eth.set_gas_price_strategy(gas_price_strategy)
        else:
            self._web3.eth.set_gas_price_strategy(fast_gas_price_strategy)

        self._transaction_callback: Optional[Callable[[TransactionLogEntry], None]] = None

    @property
    def chain_id(self) -> int:
        return self._chain_id

    @property
    def gas_price(self) -> int:
        if self._gas_price is not None:
            return self._gas_price
        else:
            gas_price = self._web3.eth.generate_gas_price()
            if gas_price is not None:
                return int(gas_price)
            else:
                raise RuntimeError('Could not determine gas price')

    def deploy_contract(self, account: Account, contract: Contract, allow_failure: bool = False,
                        *args: Any, **kwargs: Any) -> None:
        """Deploys the given contract to the environment.

        Calling this method will set the address property of the contract object on success.

        Args:
            account (Account): Account to be used for deployment.
            contract (Contract): Contract object containing the contract to be deployed.
            allow_failure (bool): Do not throw an Exception when the deployment transaction fails.
            *args (Any): Positional arguments for the contract's constructor.
            **kwargs (Any): Keyword arguments for the contract's constructor.

        Returns:
            None
        """
        web3_contract = self._web3.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
        tx_receipt = self._send_transaction(
            account=account,
            factory=web3_contract.constructor(*args, **kwargs),
            description='Contract Deployment',
            allow_failure=allow_failure
        )
        contract.address = tx_receipt['contractAddress']

    def send_contract_transaction(self, contract: Contract, account: Account, method: str, *args: Any,
                                  value: int = 0, item_share_indicator_amount: float = 0,
                                  item_share_indicator_beneficiary: Optional[Account] = None,
                                  allow_failure: bool = False, **kwargs: Any) -> Any:
        logger.debug('Preparing contract transaction %s(%s)' % (method, ', '.join([str(a) for a in [*args]])))
        web3_contract = self._web3.eth.contract(address=contract.address, abi=contract.abi)
        contract_method = getattr(web3_contract.functions, method)
        factory = contract_method(*args, **kwargs)
        self._send_transaction(
            account=account,
            factory=factory,
            value=value,
            item_share_indicator_amount=item_share_indicator_amount,
            item_share_indicator_beneficiary=item_share_indicator_beneficiary,
            description=method,
            allow_failure=allow_failure
        )
        # TODO implement contract return value

    def send_direct_transaction(self, account: Account, to: Account, value: int = 0,
                                allow_failure: bool = False) -> None:
        self._send_transaction(
            account=account,
            to=to,
            value=value,
            description='direct transfer',
            allow_failure=allow_failure
        )

    def _send_transaction(self, account: Account, factory: Optional[Any] = None, to: Optional[Account] = None,
                          value: int = 0, item_share_indicator_amount: float = 0,
                          item_share_indicator_beneficiary: Optional[Account] = None, description: Optional[str] = None,
                          allow_failure: bool = False) -> AttributeDict[str, Any]:
        if not item_share_indicator_amount == 0 and item_share_indicator_beneficiary is None:
            raise ValueError('when sharing item, beneficiary must be defined')

        tx_dict = {
            'from': account.wallet_address,
            'nonce': self._web3.eth.get_transaction_count(account.wallet_address, 'pending'),
            'value': value,
            'chainId': self._chain_id,
            'gas': 4000000
        }
        if to is not None:
            tx_dict['to'] = to.wallet_address

        if factory is not None:
            tx_dict = factory.buildTransaction(tx_dict)
        else:
            tx_dict['gas'] = 21000

        if self._gas_price is not None:
            tx_dict['gasPrice'] = self._gas_price
        else:
            tx_dict['gasPrice'] = self._web3.eth.generate_gas_price(tx_dict)
        tx_signed = self._web3.eth.account.sign_transaction(tx_dict, private_key=account.wallet_private_key)

        # collect current account balances
        balances_before: Dict[Account, int] = {}
        for tmp_account in self.seller, self.buyer, self.operator:
            balances_before.update({tmp_account: self._web3.eth.get_balance(tmp_account.wallet_address, 'latest')})

        logger.debug('Submitting transaction %s...' % str(tx_dict))
        tx_hash = self._web3.eth.send_raw_transaction(tx_signed.rawTransaction)

        tx_receipt = None
        while tx_receipt is None:
            logger.debug('Waiting for transaction receipt (hash is %s)...' % str(tx_hash.hex()))
            try:
                tx_receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)
            except TimeExhausted:
                pass

        if not allow_failure and not tx_receipt['status']:
            raise RuntimeError('Transaction execution not successful')

        logger.debug('Got receipt %s' % str(tx_receipt))

        # collect current account balances
        funds_diff_collection = FundsDiffCollection()
        for tmp_account in self.seller, self.buyer, self.operator:
            balance_after = self._web3.eth.get_balance(tmp_account.wallet_address, 'latest')
            balance_diff = balance_after - balances_before.get(tmp_account)
            if balance_diff != 0:
                funds_diff_collection += FundsDiffCollection({tmp_account: balance_diff})

        # adjustment for paid transaction fees (should NOT be contained in FundsDiffCollection, therefore re-adding)
        funds_diff_collection += FundsDiffCollection({account: tx_receipt['gasUsed'] * 1000000000})

        if not funds_diff_collection.is_neutral:
            logger.debug('Funds diff: %s' % ', '.join(['%s: %i' % (k, v) for k, v in funds_diff_collection.items()]))

        if item_share_indicator_amount == 0:
            item_share_collection = ItemShareCollection()
        else:
            item_share_collection = ItemShareCollection({
                account: -item_share_indicator_amount,
                item_share_indicator_beneficiary: item_share_indicator_amount
            })

        if self.transaction_callback is not None:
            self.transaction_callback(TransactionLogEntry(account, tx_dict, dict(tx_receipt), description,
                                                          funds_diff_collection, item_share_collection))
        return tx_receipt

    def indicate_item_share(self, account: Account, amount: float, beneficiary: Optional[Account]) -> None:
        if amount == 0:
            raise ValueError('there is no sense in indicating item share with zero amount')

        if beneficiary is None:
            raise ValueError('when sharing item, beneficiary must be defined')

        if self.transaction_callback is not None:
            self.transaction_callback(TransactionLogEntry(
                account=account,
                tx_dict={'gasPrice': 0},
                tx_receipt={'gasUsed': 0},
                description='item share',
                funds_diff_collection=FundsDiffCollection(),
                item_share_collection=ItemShareCollection({
                    account: -amount,
                    beneficiary: amount
                })
            ))

    def event_filter(self, contract: Contract, event_name: str, event_args: Optional[List[Any]] = None,
                     from_block: Union[str, int] = 'latest', to_block: Union[str, int] = 'latest',
                     address: Optional[str] = None, argument_filters: Optional[Dict[str, Any]] = None,
                     ) -> Generator[AttributeDict[str, Any], None, None]:
        if event_args is None:
            event_args = []

        if isinstance(from_block, int):
            if from_block < 0:
                from_block = self._web3.eth.getBlock('latest')['number'] + from_block

        if isinstance(to_block, int):
            if to_block < 0:
                to_block = self._web3.eth.getBlock('latest')['number'] + to_block

        web3_contract = self._web3.eth.contract(address=contract.address, abi=contract.abi)
        event_class = getattr(web3_contract.events, event_name)
        event_instance = event_class(*event_args)
        event_filter = event_instance.createFilter(
            fromBlock=from_block,
            toBlock=to_block,
            address=address,
            argument_filters=argument_filters
        )
        while True:
            for event in event_filter.get_new_entries():
                yield event
            time.sleep(0.1)

    def wait(self, seconds: int) -> None:
        timeout = self._web3.eth.getBlock('latest').timestamp + seconds
        logger.debug('Waiting for %d seconds' % seconds)
        time.sleep(seconds)  # wake up earlier
        while True:
            current = self._web3.eth.getBlock('latest').timestamp
            if current > timeout:
                return
            else:
                logger.debug('Still waiting for timeout (current: %s, waiting for: %s)' % (
                    datetime.fromtimestamp(current).isoformat(),
                    datetime.fromtimestamp(timeout).isoformat()
                ))
                time.sleep(3)

    @property
    def operator(self) -> Account:
        return self._operator

    @property
    def seller(self) -> Account:
        return self._seller

    @property
    def buyer(self) -> Account:
        return self._buyer

    @property
    def web3(self) -> Web3:
        return self._web3

    @property
    def transaction_callback(self) -> Optional[
        Callable[[TransactionLogEntry], None]
    ]:
        return self._transaction_callback

    @transaction_callback.setter
    def transaction_callback(self, callback: Optional[
        Callable[[TransactionLogEntry], None]
    ]) -> None:
        self._transaction_callback = callback
