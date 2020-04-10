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

from web3 import HTTPProvider, WebsocketProvider, IPCProvider
from . import BlockchainEnvironment, EnvironmentManager


class Web3Environment(BlockchainEnvironment):
    def __init__(self, web3_provider_class, chain_id, gas_price=None, gas_price_factor=1, gas_limit=None,
                 tx_wait_timeout=120, **kwargs):
        super(Web3Environment, self).__init__(
            web3_provider_class(**kwargs),
            chain_id=chain_id,
            gas_price=gas_price,
            gas_price_factor=gas_price_factor,
            gas_limit=gas_limit,
            tx_wait_timeout=tx_wait_timeout
        )

    def set_up(self):
        pass

    def strip_down(self):
        pass


EnvironmentManager.register('Web3HTTP', Web3Environment, HTTPProvider)
EnvironmentManager.register('Web3Websocket', Web3Environment, WebsocketProvider)
EnvironmentManager.register('Web3IPC', Web3Environment, IPCProvider)
