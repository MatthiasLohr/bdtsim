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
from .participants import operator, seller, buyer
from .dataprovider import DataProvider
from .environment import Environment
from .protocol import Protocol

logger = logging.getLogger(__name__)


class Simulation(object):
    def __init__(self, protocol: Protocol, environment: Environment, data_provider: DataProvider):
        self._protocol = protocol
        self._environment = environment
        self._data_provider = data_provider

        self._iteration_queue = Queue()

        if self._protocol.contract_is_reusable:
            self._environment.deploy_contract(operator, self._protocol.contract)

    def run(self):
        while not self._iteration_queue.empty():
            current_iteration = self._iteration_queue.get(block=False)

            if not self._protocol.contract_is_reusable:
                self._environment.deploy_contract(operator, self._protocol.contract)

            self._protocol.prepare_environment(self._environment, operator)
            self._protocol.run(self._environment, seller, buyer)
            self._protocol.cleanup_environment(self._environment, operator)
            self._iteration_queue.task_done()
