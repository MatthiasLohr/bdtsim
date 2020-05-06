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

from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.participant import buyer, operator, seller
from bdtsim.protocol import Protocol
from bdtsim.protocol_path import ProtocolPath
from .result import IterationResult, SimulationResult, PreparationResult


logger = logging.getLogger(__name__)


class Simulation(object):
    def __init__(self, protocol: Protocol, environment: Environment, data_provider: DataProvider,
                 price: int = 1000000000) -> None:
        self._protocol = protocol
        self._environment = environment
        self._data_provider = data_provider
        self._price = price

        self._protocol_path_queue: Queue[ProtocolPath] = Queue()

    def run(self) -> SimulationResult:
        logger.debug('Preparing environment for simulation...')
        self._environment.clear_transaction_logs()
        self._protocol.prepare_simulation(self._environment, operator)
        preparation_result = PreparationResult(self._environment.transaction_logs)
        logger.debug('Finished preparing the environment for simulation')

        iteration_results = []
        self._protocol_path_queue.put(ProtocolPath())
        logger.debug('Starting simulation loop')
        while not self._protocol_path_queue.empty():
            protocol_path = self._protocol_path_queue.get(block=False)
            logger.debug('Simulation will follow path %s' % str(protocol_path))

            logger.debug('Preparing environment for iteration...')
            self._environment.clear_transaction_logs()
            self._protocol.prepare_iteration(self._environment, operator)
            preparation_transaction_logs = self._environment.transaction_logs
            logger.debug('Finished preparing the environment for iteration')

            logger.debug('Starting protocol execution...')
            self._environment.clear_transaction_logs()
            self._protocol.execute(
                protocol_path=protocol_path,
                environment=self._environment,
                data_provider=self._data_provider,
                seller=seller,
                buyer=buyer,
                price=self._price
            )
            execution_transaction_logs = self._environment.transaction_logs
            logger.debug('Finished protocol execution')

            logger.debug('Starting cleanup for iteration...')
            self._environment.clear_transaction_logs()
            self._protocol.cleanup_iteration(self._environment, operator)
            cleanup_transaction_logs = self._environment.transaction_logs
            logger.debug('Finished cleaning up the iteration')

            iteration_results.append(IterationResult(
                protocol_path=protocol_path,
                preparation_transaction_logs=preparation_transaction_logs,
                execution_transaction_logs=execution_transaction_logs,
                cleanup_transaction_logs=cleanup_transaction_logs
            ))

            logger.debug('Collecting alternative paths...')

            for alternative_path in protocol_path.get_alternatives():
                self._protocol_path_queue.put(alternative_path)
                logger.debug('Added new path %s' % str(alternative_path))

            self._protocol_path_queue.task_done()

        logger.debug('Simulation finished. Cleaning up...')
        self._protocol.cleanup_simulation(self._environment, operator)
        logger.debug('Finished cleaning up the simulation')
        return SimulationResult(
            operator=operator,
            seller=seller,
            buyer=buyer,
            preparation_result=preparation_result,
            iteration_results=iteration_results
        )
