# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2021 Matthias Lohr <mail@mlohr.com>
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

import argparse
import logging
import multiprocessing
import os
from multiprocessing.pool import ApplyResult
from typing import Any, Dict, Optional, Tuple
from queue import Queue

import yaml

from bdtsim.account import AccountFile
from bdtsim.data_provider import DataProviderManager
from bdtsim.environment import EnvironmentManager
from bdtsim.protocol import ProtocolManager, DEFAULT_ASSET_PRICE
from bdtsim.renderer import RendererManager
from bdtsim.simulation import Simulation
from bdtsim.simulation_result import SimulationResult, SimulationResultSerializer
from bdtsim.util.types import to_bool
from .command_manager import SubCommand


DEFAULT_ENVIRONMENT_CONFIGURATION: Dict[str, Any] = {'name': 'PyEVM'}
DEFAULT_DATA_PROVIDER_CONFIGURATION: Dict[str, Any] = {'name': 'RandomDataProvider'}

logger = logging.getLogger(__name__)


class BulkExecuteSubCommand(SubCommand):
    help = 'bulk execute simulations and renderings'

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(BulkExecuteSubCommand, self).__init__(parser)
        parser.add_argument('bulk_configuration')
        parser.add_argument('-p', '--processes', type=int, default=multiprocessing.cpu_count())

    def __call__(self, args: argparse.Namespace) -> Optional[int]:
        with open(args.bulk_configuration, 'r') as fp:
            bulk_configuration = yaml.load(fp, Loader=yaml.SafeLoader)

        logger.info('creating process pool with %i processes' % args.processes)
        process_pool = multiprocessing.Pool(processes=args.processes)
        processes: Queue[ApplyResult[Any]] = Queue()

        simulation_configurations = bulk_configuration.get('simulations')
        if not isinstance(simulation_configurations, list):
            raise ValueError('simulations is not a list')

        renderer_configurations = bulk_configuration.get('renderers')
        if not isinstance(simulation_configurations, list):
            raise ValueError('renderers is not a list')

        target_directory = bulk_configuration.get('target_directory', 'bulk_output')
        os.makedirs(target_directory, exist_ok=True)

        def renderer_success_callback(params: Tuple[Dict[str, Any], Dict[str, Any], bytes]) -> None:
            sim_conf, renderer_conf, result = params
            logger.info('renderer succeeded (%s, %s)' % (str(sim_conf), str(renderer_conf)))
            with open(os.path.join(
                target_directory,
                self.get_output_filename(sim_conf, renderer_conf, suffix=renderer_conf.get('suffix'))
            ), 'wb') as f:
                f.write(result)

        def renderer_error_callback(error: BaseException) -> None:
            logger.warning('renderer error: %s' % str(error))

        def simulation_success_callback(params: Tuple[Dict[str, Any], SimulationResult]) -> None:
            local_simulation_configuration, result = params
            logger.info('simulation succeeded (%s)' % str(local_simulation_configuration))
            logger.debug('writing down result')
            with open(os.path.join(
                    target_directory,
                    self.get_output_filename(local_simulation_configuration, suffix='result')
            ), 'wb') as f:
                simulation_result_serializer = SimulationResultSerializer(
                    compression=to_bool(bulk_configuration.get('output_compression', True)),
                    b64encoding=to_bool(bulk_configuration.get('output_b64encoding', True))
                )
                f.write(simulation_result_serializer.serialize(result))

            logger.debug('scheduling renderers')
            for renderer_configuration in renderer_configurations:
                processes.put(process_pool.apply_async(
                    func=self.run_renderer,
                    kwds={
                        'simulation_configuration': local_simulation_configuration,
                        'renderer_configuration': renderer_configuration,
                        'simulation_result': result
                    },
                    callback=renderer_success_callback,
                    error_callback=renderer_error_callback
                ))

        def simulation_error_callback(error: BaseException) -> None:
            logger.warning('simulation error callback called: %s' % str(error))

        logger.debug('scheduling simulations')
        for simulation_configuration in simulation_configurations:
            processes.put(process_pool.apply_async(
                func=self.run_simulation,
                kwds={
                    'simulation_configuration': simulation_configuration
                },
                callback=simulation_success_callback,
                error_callback=simulation_error_callback
            ))

        while not processes.empty():
            process = processes.get(block=True)
            process.wait()

        return 0

    @staticmethod
    def run_simulation(simulation_configuration: Dict[str, Any]) -> Tuple[Dict[str, Any], SimulationResult]:
        protocol_configuration = simulation_configuration.get('protocol')
        environment_configuration = simulation_configuration.get('environment')
        data_provider_configuration = simulation_configuration.get('data_provider')

        if protocol_configuration is None:
            raise ValueError('missing protocol configuration')
        if environment_configuration is None:
            environment_configuration = DEFAULT_ENVIRONMENT_CONFIGURATION
        if data_provider_configuration is None:
            data_provider_configuration = DEFAULT_DATA_PROVIDER_CONFIGURATION

        protocol = ProtocolManager.instantiate(
            name=protocol_configuration.get('name', ''),
            **protocol_configuration.get('parameters', {})
        )

        account_file = AccountFile(simulation_configuration.get('account_file'))

        environment = EnvironmentManager.instantiate(
            name=environment_configuration.get('name', ''),
            operator=account_file.operator,
            seller=account_file.seller,
            buyer=account_file.buyer,
            **environment_configuration.get('parameters', {})
        )

        data_provider = DataProviderManager.instantiate(
            name=data_provider_configuration.get('name', ''),
            **data_provider_configuration.get('parameters', {})
        )

        simulation = Simulation(
            protocol=protocol,
            environment=environment,
            data_provider=data_provider,
            operator=account_file.operator,
            seller=account_file.seller,
            buyer=account_file.buyer,
            protocol_path_coercion=simulation_configuration.get('protocol_path'),
            price=simulation_configuration.get('price', DEFAULT_ASSET_PRICE),
        )

        simulation_result = simulation.run()
        return simulation_configuration, simulation_result

    @staticmethod
    def run_renderer(simulation_configuration: Dict[str, Any], renderer_configuration: Dict[str, Any],
                     simulation_result: SimulationResult) -> Tuple[Dict[str, Any], Dict[str, Any], bytes]:
        renderer = RendererManager.instantiate(
            name=renderer_configuration.get('name', ''),
            **renderer_configuration.get('parameters', {})
        )
        result = renderer.render(simulation_result)
        return simulation_configuration, renderer_configuration, result

    @staticmethod
    def get_output_filename(simulation_configuration: Dict[str, Any],
                            renderer_configuration: Optional[Dict[str, Any]] = None,
                            suffix: Optional[str] = None) -> str:
        def component2str(component_config: Dict[str, Any]) -> str:
            result = str(component_config.get('name'))
            parameter_lines = []
            for key, value in component_config.get('parameters', {}).items():
                parameter_lines.append('%s=%s' % (key, value))
            if len(parameter_lines):
                result += '-%s' % '-'.join(parameter_lines)
            return result

        output = '_'.join([
            component2str(simulation_configuration.get('protocol', {})),
            component2str(simulation_configuration.get('environment', {})),
            component2str(simulation_configuration.get('data_provider', DEFAULT_DATA_PROVIDER_CONFIGURATION))
        ])

        if renderer_configuration is not None:
            output += '_%s' % component2str(renderer_configuration)

        if suffix is not None:
            output += '.%s' % suffix

        return output
