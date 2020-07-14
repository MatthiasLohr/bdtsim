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
from typing import Callable, Optional

from eth_tester import EthereumTester, PyEVMBackend  # type: ignore
from eth_tester.backends import pyevm  # type: ignore
from web3 import EthereumTesterProvider, Web3
from web3.types import TxParams, Wei

from bdtsim.account import Account
from .environment import Environment
from .environment_manager import EnvironmentManager


logger = logging.getLogger(__name__)


class PyEVMEnvironment(Environment):
    def __init__(self, operator: Account, seller: Account, buyer: Account, chain_id: Optional[int] = None,
                 gas_price: Optional[int] = None,
                 gas_price_strategy: Optional[Callable[[Web3, Optional[TxParams]], Wei]] = None,
                 tx_wait_timeout: int = 120) -> None:
        if chain_id is not None and chain_id != 61:
            logger.warning('Ignoring chainId %d since PyEVM always uses chainId 61' % chain_id)

        self._pyevm_instance = self.create_pyevm_instance()
        self._eth_tester_instance = self.create_eth_tester_instance(self._pyevm_instance)

        if gas_price_strategy is None:
            gas_price_strategy = pyevm_gas_price_strategy

        super(PyEVMEnvironment, self).__init__(
            operator=operator,
            seller=seller,
            buyer=buyer,
            web3_provider=EthereumTesterProvider(self._eth_tester_instance),
            chain_id=chain_id,
            gas_price=gas_price,
            gas_price_strategy=gas_price_strategy
        )

        for account_index, recipient in [(0, self.operator), (1, self.seller), (2, self.buyer)]:
            account = self._eth_tester_instance.get_accounts()[account_index]
            self._eth_tester_instance.send_transaction({
                'from': account,
                'to': recipient.wallet_address,
                'gas': 21000,
                'value': self._eth_tester_instance.get_balance(account)-21000
            })

    def wait(self, seconds: int) -> None:
        timeout = self._web3.eth.getBlock('latest').timestamp + seconds
        self._eth_tester_instance.time_travel(timeout)

    @staticmethod
    def create_eth_tester_instance(pyevm_instance: PyEVMBackend) -> EthereumTester:
        return EthereumTester(pyevm_instance)

    @staticmethod
    def create_pyevm_instance() -> PyEVMBackend:
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


def pyevm_gas_price_strategy(web3: Web3, transaction_params: Optional[TxParams]) -> Wei:
    """
    https://web3py.readthedocs.io/en/stable/gas_price.html#creating-a-gas-price-strategy
    """
    return Wei(1000000000)


EnvironmentManager.register('PyEVM', PyEVMEnvironment)
