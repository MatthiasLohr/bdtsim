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
from typing import Optional
from web3 import Web3
from ..participant import Participant
from ..contract import Contract

logger = logging.getLogger(__name__)


class Environment(object):
    def __init__(self, web3_provider, chain_id, gas_price=None, gas_price_factor=1, tx_wait_timeout=120):
        self._web3 = Web3(web3_provider)

        self._chain_id = chain_id
        self._gas_price = gas_price
        self._gas_price_factor = gas_price_factor
        self._tx_wait_timeout = tx_wait_timeout

        self._contract = None
        self._contract_address = None

        self._transaction_log = []

    @property
    def chain_id(self):
        return self._chain_id

    @property
    def gas_price(self):
        return self._gas_price

    @property
    def gas_price_factor(self):
        return self._gas_price_factor

    @property
    def tx_wait_timeout(self):
        return self._tx_wait_timeout

    @property
    def transaction_log(self):
        return self._transaction_log

    def clear_transaction_log(self):
        self._transaction_log = []

    def deploy_contract(self, account: Participant, contract: Contract) -> None:
        web3_contract = self._web3.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
        tx_receipt = self._send_transaction(account, web3_contract.constructor())
        self._contract_address = tx_receipt['contractAddress']
        logger.debug('New contract address: %s' % self._contract_address)
        self._contract = contract

    def send_contract_transaction(self, account: Participant, method, *args, value: int = 0):
        web3_contract = self._web3.eth.contract(address=self._contract_address, abi=self._contract.abi)
        contract_method = getattr(web3_contract.functions, method)
        factory = contract_method(*args)
        return self._send_transaction(
            account=account,
            factory=factory,
            value=value
        )

    def send_direct_transaction(self, account: Participant, to: Participant, value: int = 0):
        return self._send_transaction(
            account=account,
            to=to,
            value=value
        )

    def _send_transaction(self, account: Participant, factory=None, to: Optional[Participant] = None, value: int = 0):
        gas_price = self.gas_price
        if gas_price is None:
            gas_price = self._web3.eth.gasPrice
        tx_dict = {
            'from': account.wallet_address,
            'nonce': self._web3.eth.getTransactionCount(account.wallet_address, 'pending'),
            'value': value,
            'gasPrice': int(gas_price * self._gas_price_factor),
            'chainId': self._chain_id
        }
        if to is not None:
            tx_dict['to'] = to.wallet_address
        if factory is not None:
            tx_dict = factory.buildTransaction(tx_dict)
        else:
            tx_dict['gas'] = 21000
        tx_signed = self._web3.eth.account.sign_transaction(tx_dict, private_key=account.wallet_private_key)
        tx_hash = self._web3.eth.sendRawTransaction(tx_signed.rawTransaction)
        tx_receipt = self._web3.eth.waitForTransactionReceipt(tx_hash, self.tx_wait_timeout)
        logger.debug('Successfully submitted transaction: %s' % str(tx_receipt))
        self._transaction_log.append((account, tx_receipt))
        return tx_receipt
