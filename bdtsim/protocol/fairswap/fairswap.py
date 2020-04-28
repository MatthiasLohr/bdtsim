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
from typing import Optional

from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.contract import Contract
from bdtsim.environment import Environment
from bdtsim.participant import Participant
from bdtsim.protocol_path import ProtocolPath


class FairSwap(Protocol):
    def __init__(self) -> None:
        super(FairSwap, self).__init__()

    @property
    def contract(self) -> Optional[Contract]:
        return None

    def run(self, protocol_path: ProtocolPath, environment: Environment, seller: Participant,
            buyer: Participant) -> None:
        pass


ProtocolManager.register('FairSwap-FileSale', FairSwap)
ProtocolManager.register('FairSwap-RepeatableFileSale', FairSwap)
