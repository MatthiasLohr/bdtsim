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
from .. import Protocol, ProtocolManager
from ...contract import SolidityContract
from ... import Environment, Participant
from ...protocol_path import ProtocolPath

logger = logging.getLogger(__name__)


class SimplePayment(Protocol):
    def __init__(self, use_contract: bool) -> None:
        super(SimplePayment, self).__init__(contract_is_reusable=True)

        self._use_contract = use_contract

    @property
    def contract(self) -> Optional[SolidityContract]:
        if self._use_contract:
            return SolidityContract(self.contract_path(__file__, 'SimplePayment.sol'), 'SimplePayment')
        else:
            return None

    def run(self, protocol_path: ProtocolPath, environment: Environment, seller: Participant, buyer: Participant)\
            -> None:
        if protocol_path.decide(buyer):
            logger.debug('Decided to be honest')
            if self._use_contract:                                                       # TODO parameterize value
                environment.send_contract_transaction(buyer, 'pay', seller.wallet_address, value=1000000000)
            else:
                environment.send_direct_transaction(buyer, seller, 1000000000)  # TODO parameterize value
        else:
            logger.debug('Decided to cheat')  # do nothing


ProtocolManager.register('SimplePayment', SimplePayment, use_contract=True)
ProtocolManager.register('SimplePayment-direct', SimplePayment, use_contract=False)
