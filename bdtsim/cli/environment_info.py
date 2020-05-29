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

from bdtsim.environment import EnvironmentManager
from .command_manager import SubCommand


class EnvironmentInfoSubCommand(SubCommand):
    help = 'print information about the selected environment'

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(EnvironmentInfoSubCommand, self).__init__(parser)
        parser.add_argument('environment', choices=EnvironmentManager.environments.keys())
        parser.add_argument('-e', '--environment-parameter', nargs=2, action='append', dest='environment_parameters',
                            default=[], metavar=('KEY', 'VALUE'), help='Pass additional parameters to the environment')

    def __call__(self, args: argparse.Namespace) -> int:
        environment_parameters: Dict[str, str] = {}
        for key, value in args.environment_parameters:
            environment_parameters[key.replace('-', '_')] = value

        environment = EnvironmentManager.instantiate(
            args.environment,
            **environment_parameters
        )

        print('Client version: %s' % environment.web3.clientVersion)
        syncing = environment.web3.eth.syncing
        if not syncing:
            print('Sync Status: not syncing')
        elif not isinstance(syncing, bool):
            print('Sync Status: syncing (%d/%d)' % (syncing.currentBlock, syncing.highestBlock))

        print('Chain ID: %s' % str(environment.web3.eth.chainId))
        return 0
