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
from eth_tester import EthereumTester, PyEVMBackend
from eth_tester.backends import pyevm
from web3 import EthereumTesterProvider
from . import Environment, EnvironmentManager
from ..participant import operator, seller, buyer

logger = logging.getLogger(__name__)


class PyEVMEnvironment(Environment):
    def __init__(self, chain_id, gas_price=None, gas_price_factor=1, tx_wait_timeout=120):
        if chain_id != 61:
            logger.warning('Ignoring chainId %d since PyEVM always uses chainId 61' % chain_id)

        self._pyevm_instance = self.create_pyevm_instance()
        self._eth_tester_instance = self.create_eth_tester_instance(self._pyevm_instance)

        super(PyEVMEnvironment, self).__init__(
            EthereumTesterProvider(self._eth_tester_instance),
            chain_id=61,
            gas_price=gas_price,
            gas_price_factor=gas_price_factor,
            tx_wait_timeout=tx_wait_timeout
        )

        for account_index, recipient in [(0, operator), (1, seller), (2, buyer)]:
            account = self._eth_tester_instance.get_accounts()[account_index]
            self._eth_tester_instance.send_transaction({
                'from': account,
                'to': recipient.wallet_address,
                'gas': 21000,
                'value': self._eth_tester_instance.get_balance(account)-21000
            })

    @staticmethod
    def create_eth_tester_instance(pyevm_instance):
        return EthereumTester(pyevm_instance)

    @staticmethod
    def create_pyevm_instance():
        return PyEVMBackend({
            'bloom': 0,
            'coinbase': pyevm.main.GENESIS_COINBASE,
            'difficulty': pyevm.main.GENESIS_DIFFICULTY,
            'extra_data': pyevm.main.GENESIS_EXTRA_DATA,
            'gas_limit': 8000000,
            'gas_used': 0,
            'mix_hash': pyevm.main.GENESIS_MIX_HASH,
            'nonce': pyevm.main.GENESIS_NONCE,
            'block_number': pyevm.main.GENESIS_BLOCK_NUMBER,
            'parent_hash': pyevm.main.GENESIS_PARENT_HASH,
            'receipt_root': pyevm.main.BLANK_ROOT_HASH,
            'timestamp': int(time.time()),
            'transaction_root': pyevm.main.BLANK_ROOT_HASH,
            'uncles_hash': pyevm.main.EMPTY_RLP_LIST_HASH
        })


EnvironmentManager.register('PyEVM', PyEVMEnvironment)
