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
from .. import Protocol, ProtocolManager
from ...contract import SolidityContract

logger = logging.getLogger(__name__)


class SimplePayment(Protocol):
    def __init__(self, use_contract):
        super(SimplePayment, self).__init__(contract_is_reusable=True)

        self._use_contract = use_contract

    @property
    def contract(self):
        if self._use_contract:
            return SolidityContract(self.contract_path(__file__, 'SimplePayment.sol'), 'SimplePayment')
        else:
            return None

    def run(self, environment, seller, buyer):
        if buyer.decide():
            logger.debug('Decided to be honest')
            if self._use_contract:
                environment.send_contract_transaction()
                # todo continue
            else:
                environment.send_direct_transaction()
                # todo continue
        else:
            logger.debug('Decided to cheat')  # just doing nothing


ProtocolManager.register('SimplePayment-direct', SimplePayment, use_contract=False)
ProtocolManager.register('SimplePayment-indirect', SimplePayment, use_contract=True)
