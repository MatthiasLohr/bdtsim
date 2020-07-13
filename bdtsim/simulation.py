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

from bdtsim.account import Account
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol
from bdtsim.protocol_path import ProtocolPath
from bdtsim.output import SimulationResult, ResultCollector


logger = logging.getLogger(__name__)


class Simulation(object):
    def __init__(self, protocol: Protocol, environment: Environment, data_provider: DataProvider, operator: Account,
                 seller: Account, buyer: Account, price: int = 1000000000) -> None:
        self._protocol = protocol
        self._environment = environment
        self._data_provider = data_provider
        self._operator = operator
        self._seller = seller
        self._buyer = buyer
        self._price = price

        self._protocol_path_queue: Queue[ProtocolPath] = Queue()

    def run(self) -> SimulationResult:
        result_collector = ResultCollector(self._operator, self._seller, self._buyer)

        logger.debug('Preparing environment for simulation...')
        with result_collector.monitor_preparation(self._environment):
            self._protocol.prepare_simulation(self._environment, self._operator)
        logger.debug('Finished preparing the environment for simulation')

        self._protocol_path_queue.put(ProtocolPath())
        logger.debug('Starting simulation loop')
        while not self._protocol_path_queue.empty():
            protocol_path = self._protocol_path_queue.get(block=False)

            with result_collector.monitor_execution(self._environment, protocol_path):
                logger.debug('Simulation will follow path %s' % str(protocol_path))

                logger.debug('Preparing environment for iteration...')
                self._protocol.prepare_iteration(self._environment, self._operator)
                logger.debug('Finished preparing the environment for iteration')

                self._data_provider.file_pointer.seek(0, 0)
                logger.debug('Starting protocol execution...')
                self._protocol.execute(
                    protocol_path=protocol_path,
                    environment=self._environment,
                    data_provider=self._data_provider,
                    seller=self._seller,
                    buyer=self._buyer,
                    price=self._price
                )
                logger.debug('Finished protocol execution')

                logger.debug('Starting cleanup for iteration...')
                self._protocol.cleanup_iteration(self._environment, self._operator)
                logger.debug('Finished cleaning up the iteration')

                logger.debug('Collecting alternative paths...')

                for alternative_path in protocol_path.get_alternatives():
                    self._protocol_path_queue.put(alternative_path)
                    logger.debug('Added new path %s' % str(alternative_path))

            self._protocol_path_queue.task_done()

        logger.debug('Simulation finished. Cleaning up...')
        self._protocol.cleanup_simulation(self._environment, self._operator)
        logger.debug('Finished cleaning up the simulation')
        return result_collector.simulation_result
