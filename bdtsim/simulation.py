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
from .participant import operator, seller, buyer
from .data_provider import DataProvider
from .environment import Environment
from .protocol import Protocol
from .protocol_path import ProtocolPath
from .simulation_result_collector import SimulationResultCollector

logger = logging.getLogger(__name__)


class Simulation(object):
    def __init__(self, protocol: Protocol, environment: Environment, data_provider: DataProvider):
        self._protocol = protocol
        self._environment = environment
        self._data_provider = data_provider

        self._protocol_path_queue: "Queue[ProtocolPath]" = Queue()

    def run(self):
        result_collector = SimulationResultCollector()

        # single initial contract deployment?
        self._environment.clear_transaction_log()
        if self._protocol.contract_is_reusable and self._protocol.contract is not None:
            self._environment.clear_transaction_log()
            self._environment.deploy_contract(operator, self._protocol.contract)
            result_collector.set_preparation_result(self._environment.transaction_log[0])

        self._protocol_path_queue.put(ProtocolPath())

        logger.debug('Simulation started')
        while not self._protocol_path_queue.empty():
            protocol_path = self._protocol_path_queue.get(block=False)
            self._environment.clear_transaction_log()
            logger.debug('Simulation will follow path %s' % str(protocol_path.decisions_list))

            # per-iteration contract deployment
            if not self._protocol.contract_is_reusable and self._protocol.contract is not None:
                self._environment.deploy_contract(operator, self._protocol.contract)

            logger.debug('Preparing environment...')
            self._protocol.prepare_environment(self._environment, operator)
            logger.debug('Starting protocol iteration...')
            self._protocol.run(protocol_path, self._environment, seller, buyer)
            logger.debug('Protocol iteration finished')
            result_collector.add_execution_result(protocol_path, self._environment.transaction_log)
            logger.debug('Collecting alternative paths...')
            for alternative_path in ProtocolPath.get_alternative_paths(protocol_path.new_decisions_list):
                self._protocol_path_queue.put(ProtocolPath(protocol_path.initial_decisions_list + alternative_path))
                logger.debug('Added new path %s' % str(protocol_path.initial_decisions_list + alternative_path))
            logger.debug('Cleaning up environment...')
            self._protocol.cleanup_environment(self._environment, operator)
            self._protocol_path_queue.task_done()
        logger.debug('Simulation finished')
        return result_collector
