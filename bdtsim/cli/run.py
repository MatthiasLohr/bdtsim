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
from typing import Dict

from bdtsim.data_provider import DataProviderManager
from bdtsim.environment import EnvironmentManager
from bdtsim.protocol import ProtocolManager
from bdtsim.output import OutputFormatManager
from bdtsim.simulation import Simulation
from .command_manager import SubCommand


class RunSubCommand(SubCommand):
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(RunSubCommand, self).__init__(parser)
        parser.add_argument('protocol', choices=ProtocolManager.protocols.keys())
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys())
        parser.add_argument('--data-provider', choices=DataProviderManager.data_providers.keys(),
                            default='RandomDataProvider')
        parser.add_argument('-c', '--chain-id', type=int, default=None)
        parser.add_argument('-f', '--output-format', choices=OutputFormatManager.output_formats.keys(),
                            default='human-readable')
        parser.add_argument('--price', type=int, default=1000000000)
        parser.add_argument('--gas-price', type=int, default=None)
        parser.add_argument('-p', '--protocol-parameter', nargs=2, action='append', dest='protocol_parameters',
                            default=[])
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[])
        parser.add_argument('-d', '--data-provider-parameter', nargs=2, action='append',
                            dest='data_provider_parameters', default=[])
        parser.add_argument('-o', '--output-format-parameter', nargs=2, action='append',
                            dest='output_format_parameters', default=[])

    def __call__(self, args: argparse.Namespace) -> None:
        protocol_parameters: Dict[str, str] = {}
        environment_parameters: Dict[str, str] = {}
        data_provider_parameters: Dict[str, str] = {}
        output_format_parameters: Dict[str, str] = {}

        for arg, dest in [
            (args.protocol_parameters, protocol_parameters),
            (args.environment_parameters, environment_parameters),
            (args.data_provider_parameters, data_provider_parameters),
            (args.output_format_parameters, output_format_parameters),
        ]:
            for key, value in arg:
                dest[key.replace('-', '_')] = value

        protocol = ProtocolManager.instantiate(
            args.protocol,
            **protocol_parameters
        )

        environment = EnvironmentManager.instantiate(
            args.environment,
            chain_id=args.chain_id,
            gas_price=args.gas_price,
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
            price=args.price
        )

        output_format = OutputFormatManager.instantiate(
            args.output_format,
            **output_format_parameters
        )

        simulation_result = simulation.run()
        output_format.render(simulation_result)
