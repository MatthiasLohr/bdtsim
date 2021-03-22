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
import sys
from typing import Dict

from bdtsim.account import AccountFile
from bdtsim.data_provider import DataProviderManager
from bdtsim.environment import EnvironmentManager
from bdtsim.protocol import ProtocolManager, DEFAULT_ASSET_PRICE
from bdtsim.simulation import Simulation
from bdtsim.simulation_result import SimulationResultSerializer
from bdtsim.util.argparse import ProtocolPathCoercionParameter
from bdtsim.util.types import to_bool
from .command_manager import SubCommand


class RunSubCommand(SubCommand):
    help = 'run a simulation'

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(RunSubCommand, self).__init__(parser)
        parser.add_argument('protocol', choices=ProtocolManager.protocols.keys(), help='protocol to be simulated')
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys(),
                            help='environment in which the simulation will take place')
        parser.add_argument('--account-file', help='Specify an accounts file to be used')
        parser.add_argument('--protocol-path', type=ProtocolPathCoercionParameter(),
                            help='Limit protocol paths to be simulated')
        parser.add_argument('--data-provider', choices=DataProviderManager.data_providers.keys(),
                            default='RandomDataProvider', help='set the data provider/data source for the simulation')
        parser.add_argument('--price', type=int, default=DEFAULT_ASSET_PRICE,
                            help='set the price for the asset to be traded (in Wei)')
        parser.add_argument('-p', '--protocol-parameter', nargs=2, action='append', dest='protocol_parameters',
                            default=[], metavar=('KEY', 'VALUE'), help='pass additional parameters to the protocol')
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[], metavar=('KEY', 'VALUE'), help='pass additional parameters to the environment')
        parser.add_argument('-d', '--data-provider-parameter', nargs=2, action='append',
                            dest='data_provider_parameters', default=[], metavar=('KEY', 'VALUE'),
                            help='pass additional parameters to the data provider')
        parser.add_argument('-o', '--output', default='-', help='Output file to be used, default: stdout')
        parser.add_argument('--output-compression', default=True)
        parser.add_argument('--output-b64encoding', default=True)

    def __call__(self, args: argparse.Namespace) -> int:
        protocol_parameters: Dict[str, str] = {}
        environment_parameters: Dict[str, str] = {}
        data_provider_parameters: Dict[str, str] = {}

        for arg, dest in [
            (args.protocol_parameters, protocol_parameters),
            (args.environment_parameters, environment_parameters),
            (args.data_provider_parameters, data_provider_parameters)
        ]:
            for key, value in arg:
                dest[key.replace('-', '_')] = value

        protocol = ProtocolManager.instantiate(
            args.protocol,
            **protocol_parameters
        )

        account_file = AccountFile(path=args.account_file)

        environment = EnvironmentManager.instantiate(
            name=args.environment,
            operator=account_file.operator,
            seller=account_file.seller,
            buyer=account_file.buyer,
            **environment_parameters
        )

        data_provider = DataProviderManager.instantiate(
            args.data_provider,
            **data_provider_parameters
        )

        simulation = Simulation(
            protocol=protocol,
            environment=environment,
            data_provider=data_provider,
            operator=account_file.operator,
            seller=account_file.seller,
            buyer=account_file.buyer,
            protocol_path_coercion=args.protocol_path,
            price=args.price,
        )

        simulation_result = simulation.run()
        simulation_result_serializer = SimulationResultSerializer(
            compression=to_bool(args.output_compression),
            b64encoding=to_bool(args.output_b64encoding)
        )

        result_output = simulation_result_serializer.serialize(simulation_result)

        if args.output == '-':
            sys.stdout.buffer.write(result_output)
        else:
            with open(args.output, 'wb') as fp:
                fp.write(result_output)

        return 0
