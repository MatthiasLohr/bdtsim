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
from web3 import Web3
from ..protocol import Contract

logger = logging.getLogger(__name__)


class Role(object):
    wallet_address = None
    wallet_private_key = None

    def __init__(self, environment):
        self._environment = environment
        self._web3 = Web3(environment.web3_provider)
        self._gas_limit = environment.gas_limit or self._web3.eth.getBlock('latest').gasLimit
        self._gas_price = environment.gas_price or self._web3.eth.gasPrice
        self._gas_price_factor = environment.gas_price_factor or 1

    def send_transaction(self, transaction, value=0, gas_limit=None, gas_price=None, gas_price_factor=None):
        if gas_limit is None:
            gas_limit = self._gas_limit
        if gas_price is None:
            gas_price = self._gas_price
        if gas_price_factor is None:
            gas_price_factor = self._gas_price_factor
        tx_dict = {
            'from': self.wallet_address,
            'nonce': self._web3.eth.getTransactionCount(self.wallet_address, 'pending'),
            'gas': gas_limit,
            'value': value,
            'gasPrice': int(gas_price * gas_price_factor),
            'chainId': self._environment.chain_id
        }
        logger.debug('Preparing transaction ' + str(tx_dict))
        tx_unsigned = transaction.buildTransaction(tx_dict)
        tx_signed = self._web3.eth.account.sign_transaction(tx_unsigned, private_key=self.wallet_private_key)
        tx_hash = self._web3.eth.sendRawTransaction(tx_signed.rawTransaction)
        tx_receipt = self._web3.eth.waitForTransactionReceipt(tx_hash, self._environment.tx_wait_timeout)
        logger.debug('Transaction receipt: ' + str(tx_receipt))
        return tx_receipt


class Operator(Role):
    wallet_address = '0x3ed8424aaE568b3f374e94a139D755982800a4a2'
    wallet_private_key = '0xe67518b4d5255ec708d2bf9cd4222adda89fcc07037c614d7787a694fbb47692'

    def deploy_contract(self, contract):
        if not isinstance(contract, Contract):
            raise ValueError('Not a contract instance')
        web3_contract = self._web3.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
        web3_contract_tx = web3_contract.constructor()
        return self.send_transaction(web3_contract_tx)


class ActiveRole(Role):
    def __init__(self, honesty_decision_list=None, scheduler_callback=None):
        self._honesty_decision_list = honesty_decision_list or []
        self._honesty_decision_index = 0
        self._scheduler_callback = None

    def proceed_honestly(self):
        if len(self._honesty_decision_list) == self._honesty_decision_index:
            if self._scheduler_callback is not None:
                self._scheduler_callback(previously=self._honesty_decision_list, current=True)
            self._honesty_decision_list.append(True)
        decision = self._honesty_decision_list[self._honesty_decision_index]
        self._honesty_decision_index += 1
        return decision


class Seller(ActiveRole):
    wallet_address = '0x5Afa5874959ff249103c2043fB45d68B2768Fef8'
    wallet_private_key = '0x3df2d74ceb3c58a8fdb1f0ecf45e2ceb10511469d9c20691333d666fa557899a'


class Buyer(ActiveRole):
    wallet_address = '0x00c382926f098566EA6F1707296eC342E7C8A5DC'
    wallet_private_key = '0x7d96e8fbe712cf25f141adb6bc5e3244d7a19d9c406ab6ed6a097585d01b93ac'
