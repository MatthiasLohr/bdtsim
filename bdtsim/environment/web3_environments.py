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

from typing import Any, Callable, Optional, Type

from web3 import HTTPProvider, IPCProvider, Web3, WebsocketProvider
from web3.middleware.geth_poa import geth_poa_middleware
from web3.providers.base import JSONBaseProvider
from web3.types import TxParams, Wei

from bdtsim.account import Account
from .environment import Environment
from .environment_manager import EnvironmentManager


class Web3Environment(Environment):
    def __init__(self, web3_provider_class: Type[JSONBaseProvider], operator: Account, seller: Account, buyer: Account,
                 chain_id: Optional[int] = None, gas_price: Optional[int] = None,
                 gas_price_strategy: Optional[Callable[[Web3, Optional[TxParams]], Wei]] = None,
                 inject_poa_middleware: bool = False, **kwargs: Any) -> None:

        # noinspection PyArgumentList
        super(Web3Environment, self).__init__(
            web3_provider=web3_provider_class(**kwargs),  # type: ignore
            operator=operator,
            seller=seller,
            buyer=buyer,
            chain_id=chain_id,
            gas_price=gas_price,
            gas_price_strategy=gas_price_strategy
        )

        if inject_poa_middleware:
            self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def set_up(self) -> None:
        pass

    def strip_down(self) -> None:
        pass


EnvironmentManager.register('Web3HTTP', Web3Environment, HTTPProvider)
EnvironmentManager.register('Web3Websocket', Web3Environment, WebsocketProvider)
EnvironmentManager.register('Web3IPC', Web3Environment, IPCProvider)
