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
import logging
from typing import Dict, Optional, Type

import bdtsim


class SubCommand(object):
    help: Optional[str] = None

    def __init__(self, parser: argparse.ArgumentParser):
        self._parser = parser

    def __call__(self, args: argparse.Namespace) -> Optional[int]:
        raise NotImplementedError()


class CommandManager(object):
    def __init__(self) -> None:
        self._argument_parser = argparse.ArgumentParser()
        self._argument_parser.add_argument('-l', '--log-level', default='WARNING',
                                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                           help='set log level for bdtsim')
        self._command_parser = self._argument_parser.add_subparsers(title='command', dest='command', required=True)
        self._subcommands: Dict[str, SubCommand] = {}

    def register_subcommand(self, subcommand: str, cls: Type[SubCommand]) -> None:
        if not issubclass(cls, SubCommand):
            raise ValueError('cls is not a subclass of SubCommand')
        self._subcommands[subcommand] = cls(self._command_parser.add_parser(subcommand, help=cls.help))

    def get_subcommand(self, subcommand: str) -> SubCommand:
        return self._subcommands[subcommand]

    def run(self) -> Optional[int]:
        args = self._argument_parser.parse_args()
        logger = logging.getLogger(bdtsim.__name__)
        logger.setLevel(logging.getLevelName(args.log_level))
        subcommand = self.get_subcommand(args.command)
        return subcommand(args)
