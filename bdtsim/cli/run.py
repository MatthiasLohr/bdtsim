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

import argparse
import json
import yaml
from typing import Dict
from .command_manager import SubCommand
from ..data_provider import DataProviderManager
from ..environment import EnvironmentManager
from ..participant import seller, buyer
from ..protocol import ProtocolManager
from ..result import ResultSerializer
from ..simulation import Simulation


class RunSubCommand(SubCommand):
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(RunSubCommand, self).__init__(parser)
        parser.add_argument('protocol', choices=ProtocolManager.protocols.keys())
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys())
        # parser.add_argument('--data-provider', choices=DataProviderManager.data_providers.keys(),
        #                     default='GenericDataProvider')
        parser.add_argument('-c', '--chain-id', type=int, default=1)
        parser.add_argument('-o', '--output-format', choices=['human-readable', 'json', 'yaml'],
                            default='human-readable')
        parser.add_argument('--gas-price', type=int, default=None)
        parser.add_argument('--tx-wait-timeout', type=int, default=120)
        parser.add_argument('-p', '--protocol-parameter', nargs=2, action='append', dest='protocol_parameters',
                            default=[])
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[])
        # parser.add_argument('-d', '--data-provider-parameter', nargs=2, action='append',
        #                     dest='data_provider_parameters', default=[])

    def __call__(self, args: argparse.Namespace) -> None:
        protocol_parameters: Dict[str, str] = {}
        for key, value in args.protocol_parameters:
            protocol_parameters[key.replace('-', '_')] = value

        environment_parameters: Dict[str, str] = {}
        for key, value in args.environment_parameters:
            environment_parameters[key.replace('-', '_')] = value

        # data_provider_parameters: Dict[str, str] = {}
        # for key, value in args.data_provider_parameters:
        #    data_provider_parameters[key.replace('-', '_')] = value

        protocol = ProtocolManager.instantiate(
            args.protocol,
            **protocol_parameters
        )

        environment = EnvironmentManager.instantiate(
            args.environment,
            chain_id=args.chain_id,
            gas_price=args.gas_price,
            tx_wait_timeout=args.tx_wait_timeout,
            **environment_parameters
        )

        # TODO implement support for data providers
        # data_provider = DataProviderManager.instantiate(
        #     args.data_provider,
        #     **data_provider_parameters
        # )

        simulation = Simulation(
            protocol=protocol,
            environment=environment,
            data_provider=DataProviderManager.instantiate('GenericDataProvider')  # TODO replace with data_provider
        )

        simulation_result = simulation.run()
        if args.output_format == 'human-readable':
            preparation_result = simulation_result.preparation_result
            if preparation_result is not None:
                print('Preparation Costs (gas): %d (%d transaction(s))' % (
                    preparation_result.transaction_cost_sum,
                    preparation_result.transaction_count
                ))
            honest_iteration = simulation_result.completely_honest_iteration_result
            for participant in seller, buyer:
                print('%s transaction fees: %d (%d transaction(s))' % (
                    participant.name,
                    honest_iteration.transaction_fee_sum_by_participant(participant),
                    honest_iteration.transaction_count_by_participant(participant)
                ))
                # TODO calculate and show risk
        elif args.output_format == 'json':
            print(json.dumps(simulation_result, cls=ResultSerializer, indent=2))
        elif args.output_format == 'yaml':
            json_str = json.dumps(simulation_result, cls=ResultSerializer, indent=2)
            json_structure = json.loads(json_str)
            print(yaml.dump(json_structure))
