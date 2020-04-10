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
from queue import Queue
from .roles import Operator, Seller, Buyer
from ..environment import BlockchainEnvironment
from ..protocol import ProtocolRegistration

logger = logging.getLogger(__name__)


class Simulation(object):
    def __init__(self, protocol, environment):
        logger.debug('Initializing simulation')
        if not isinstance(protocol, ProtocolRegistration):
            raise ValueError('protocol need to be of type ProtocolRegistration')
        if not isinstance(environment, BlockchainEnvironment):
            raise ValueError('environment need to be of type BlockchainEnvironment')

        # store variables
        self._protocol = protocol
        self._environment = environment
        self._iterations = Queue()
        self._contract_address = None

        protocol_instance = self._protocol.instantiate()
        if protocol_instance.contract_reusable:
            protocol = self._protocol.instantiate(operator=Operator(environment))
            protocol.deploy_contract()

        # prepare iteration queue
        self._current_iteration = None

    def run(self):
        results = []
        while not self._iterations.empty():
            self._current_iteration = self._iterations.get(block=False)
            if not self._protocol.contract_reusable:
                pass  # TODO deploy smart contract
            self._iterations.task_done()
        return results
