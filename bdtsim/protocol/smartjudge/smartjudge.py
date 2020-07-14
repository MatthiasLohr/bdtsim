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

from bdtsim.account import Account
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class SmartJudge(Protocol):
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        pass


ProtocolManager.register('SmartJudge-FairSwap', SmartJudge)
