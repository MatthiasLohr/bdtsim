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
from typing import Any, Callable, List, Optional
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.gas_strategies.time_based import fast_gas_price_strategy
from web3.providers.base import BaseProvider
from web3.types import Wei, TxParams

from ..participant import Participant
from ..contract import Contract

logger = logging.getLogger(__name__)


class TransactionLogEntry(object):
    def __init__(self, account: Participant, transaction_receipt: AttributeDict[str, Any],
                 timestamp: Optional[float] = None):
        # TODO save contract method and contract method args
        self._account = account
        self._transaction_receipt = transaction_receipt
        self._timestamp = timestamp

    @property
    def account(self) -> Participant:
        return self._account

    @property
    def transaction_receipt(self) -> AttributeDict[str, Any]:
        return self._transaction_receipt

    @property
    def timestamp(self) -> Optional[float]:
        return self._timestamp


class Environment(object):
    def __init__(self, web3_provider: BaseProvider, chain_id: int, gas_price: Optional[int] = None,
                 gas_price_strategy: Optional[Callable[[Web3, Optional[TxParams]], Wei]] = None,
                 tx_wait_timeout: int = 120) -> None:
        self._web3 = Web3(web3_provider)

        self._chain_id = chain_id
        self._gas_price = gas_price
        if gas_price_strategy is not None:
            self._web3.eth.setGasPriceStrategy(gas_price_strategy)
        else:
            self._web3.eth.setGasPriceStrategy(fast_gas_price_strategy)
        self._tx_wait_timeout = tx_wait_timeout

        self._contract: Optional[Contract] = None
        self._contract_address: Optional[str] = None

        self._transaction_logs: List[TransactionLogEntry] = []

    @property
    def chain_id(self) -> int:
        return self._chain_id

    @property
    def gas_price(self) -> Optional[int]:
        return self._gas_price

    @property
    def tx_wait_timeout(self) -> int:
        return self._tx_wait_timeout

    @property
    def transaction_logs(self) -> List[TransactionLogEntry]:
        return self._transaction_logs

    def clear_transaction_logs(self) -> None:
        self._transaction_logs = []

    def deploy_contract(self, account: Participant, contract: Contract) -> None:
        web3_contract = self._web3.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
        tx_receipt = self._send_transaction(account, web3_contract.constructor())
        self._contract_address = tx_receipt['contractAddress']
        logger.debug('New contract address: %s' % self._contract_address)
        self._contract = contract

    def send_contract_transaction(self, account: Participant, method: str, *args: Any, value: int = 0) -> Any:
        if self._contract is None:
            raise RuntimeError('No contract available!')
        web3_contract = self._web3.eth.contract(address=self._contract_address, abi=self._contract.abi)
        contract_method = getattr(web3_contract.functions, method)
        factory = contract_method(*args)
        self._send_transaction(
            account=account,
            factory=factory,
            value=value
        )
        # TODO implement contract return value

    def send_direct_transaction(self, account: Participant, to: Participant, value: int = 0) -> None:
        self._send_transaction(
            account=account,
            to=to,
            value=value
        )

    def _send_transaction(self, account: Participant, factory: Optional[Any] = None, to: Optional[Participant] = None,
                          value: int = 0) -> AttributeDict[str, Any]:
        tx_dict = {
            'from': account.wallet_address,
            'nonce': self._web3.eth.getTransactionCount(account.wallet_address, 'pending'),
            'value': value,
            'chainId': self._chain_id
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
            tx_dict['gasPrice'] = self._web3.eth.generateGasPrice(tx_dict)
        tx_signed = self._web3.eth.account.sign_transaction(tx_dict, private_key=account.wallet_private_key)
        tx_hash = self._web3.eth.sendRawTransaction(tx_signed.rawTransaction)
        tx_receipt = self._web3.eth.waitForTransactionReceipt(tx_hash, self.tx_wait_timeout)
        logger.debug('Successfully submitted transaction: %s' % str(tx_receipt))
        self._transaction_logs.append(TransactionLogEntry(account, tx_receipt, time.time()))
        return tx_receipt
