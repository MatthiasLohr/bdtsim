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

from typing import Optional

from .command_manager import CommandManager
from .environment_info import EnvironmentInfoSubCommand
from .list_environments import ListEnvironmentsSubCommand
from .list_protocols import ListProtocolsSubCommand
from .list_output_formats import ListOutputFormatsSubCommand
from .list_data_providers import ListDataProvidersSubCommand
from .run import RunSubCommand


def main() -> Optional[int]:
    command_manager = CommandManager()
    command_manager.register_subcommand('list-protocols', ListProtocolsSubCommand)
    command_manager.register_subcommand('list-environments', ListEnvironmentsSubCommand)
    command_manager.register_subcommand('list-data-providers', ListDataProvidersSubCommand)
    command_manager.register_subcommand('list-output-formats', ListOutputFormatsSubCommand)
    command_manager.register_subcommand('environment-info', EnvironmentInfoSubCommand)
    command_manager.register_subcommand('run', RunSubCommand)
    return command_manager.run()
