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
from ..environment import EnvironmentManager
from ..protocol import ProtocolRegistration
from ..simulation import Simulation


class RunSubCommand(SubCommand):
    def __init__(self, parser):
        super(RunSubCommand, self).__init__(parser)
        parser.add_argument('protocol', choices=ProtocolRegistration.protocols.keys())
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys())
        parser.add_argument('-c', '--chain-id', type=int, default=1)
        parser.add_argument('--gas-price', type=int, default=None)
        parser.add_argument('--gas-price-factor', type=float, default=1)
        parser.add_argument('--gas-limit', type=int, default=None)
        parser.add_argument('--tx-wait-timeout', type=int, default=120)
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[])

    def __call__(self, args):
        environment_parameters = {}
        for key, value in args.environment_parameters:
            environment_parameters[key.replace('-', '_')] = value
        environment = EnvironmentManager.instantiate(
            args.environment,
            chain_id=args.chain_id,
            gas_price=args.gas_price,
            gas_price_factor=args.gas_price_factor,
            gas_limit=args.gas_limit,
            tx_wait_timeout = args.tx_wait_timeout,
            **environment_parameters
        )
        simulation = Simulation(
            protocol=ProtocolRegistration.protocols[args.protocol],
            environment=environment
        )
        results = simulation.run()
        print(results)
