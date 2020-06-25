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

import os
from typing import Any

from bdtsim.account import Account
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol_path import ProtocolPath


class Protocol(object):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args):
            raise TypeError('Unrecognized positional argument "%s" for Protocol' % str(args[0]))
        if len(kwargs):
            raise TypeError('Unrecognized keyword argument "%s" for Protocol' % str(list(kwargs.keys())[0]))

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        pass

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        pass

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        raise NotImplementedError()

    def cleanup_iteration(self, environment: Environment, operator: Account) -> None:
        pass

    def cleanup_simulation(self, environment: Environment, operator: Account) -> None:
        pass

    @staticmethod
    def contract_path(file_var: str, filename: str) -> str:
        return os.path.join(os.path.dirname(file_var), filename)
