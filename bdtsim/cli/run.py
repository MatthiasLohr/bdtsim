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

from .command_manager import SubCommand
from ..data_provider import DataProviderManager
from ..environment import EnvironmentManager
from ..protocol import ProtocolManager
from ..simulation import Simulation


class RunSubCommand(SubCommand):
    def __init__(self, parser):
        super(RunSubCommand, self).__init__(parser)
        parser.add_argument('protocol', choices=ProtocolManager.protocols.keys())
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys())
        # parser.add_argument('--data-provider', choices=DataProviderManager.data_providers.keys(),
        #                     default='GenericDataProvider')
        parser.add_argument('-c', '--chain-id', type=int, default=1)
        parser.add_argument('--gas-price', type=int, default=None)
        parser.add_argument('--gas-price-factor', type=float, default=1)
        parser.add_argument('--tx-wait-timeout', type=int, default=120)
        parser.add_argument('-p', '--protocol-parameter', nargs=2, action='append', dest='protocol_parameters',
                            default=[])
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[])
        # parser.add_argument('-d', '--data-provider-parameter', nargs=2, action='append',
        #                     dest='data_provider_parameters', default=[])

    def __call__(self, args):
        protocol_parameters = {}
        for key, value in args.protocol_parameters:
            protocol_parameters[key.replace('-', '_')] = value

        environment_parameters = {}
        for key, value in args.environment_parameters:
            environment_parameters[key.replace('-', '_')] = value

        # data_provider_parameters = {}
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
            gas_price_factor=args.gas_price_factor,
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

        results = simulation.run()
        print(results)  # TODO nicer results
