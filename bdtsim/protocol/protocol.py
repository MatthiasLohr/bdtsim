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
from ..roles import Role
from ..environment import Environment


class Protocol(object):
    def __init__(self, contract_is_reusable=False):
        self._contract_is_reusable = contract_is_reusable

    def run(self, environment: Environment, seller: Role, buyer: Role):
        raise NotImplementedError()

    @property
    def contract_is_reusable(self) -> bool:
        return self._contract_is_reusable

    @property
    def contract(self):
        raise NotImplementedError()

    @staticmethod
    def contract_path(file_var, filename):
        return os.path.join(os.path.dirname(file_var), filename)
