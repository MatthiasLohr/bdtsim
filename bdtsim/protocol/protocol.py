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
from ..environment import Environment
from ..participant import Participant


class Protocol(object):
    def __init__(self, contract_is_reusable=False):
        self._contract_is_reusable = contract_is_reusable

    def prepare_environment(self, environment: Environment, operator: Participant):
        pass

    def run(self, environment: Environment, seller: Participant, buyer: Participant):
        raise NotImplementedError()

    def cleanup_environment(self, environment: Environment, operator: Participant):
        pass

    @property
    def contract_is_reusable(self) -> bool:
        return self._contract_is_reusable

    @property
    def contract(self):
        raise NotImplementedError()

    @staticmethod
    def contract_path(file_var, filename):
        return os.path.join(os.path.dirname(file_var), filename)
