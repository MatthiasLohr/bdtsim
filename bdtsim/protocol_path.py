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

import itertools
from typing import Optional, List


class ProtocolPath(object):
    def __init__(self, decisions_list: Optional[List[bool]] = None):
        self._initial_decisions_list = decisions_list or []
        self._new_decisions_list = []
        self._decisions_index = 0

    def decide(self) -> bool:
        if len(self.decisions_list) == self._decisions_index:
            self._new_decisions_list.append(True)
        decision = self.decisions_list[self._decisions_index]
        self._decisions_index += 1
        return decision

    @property
    def initial_decisions_list(self) -> List[bool]:
        return self._initial_decisions_list

    @property
    def new_decisions_list(self) -> List[bool]:
        return self._new_decisions_list

    @property
    def decisions_list(self) -> List[bool]:
        return self.initial_decisions_list + self.new_decisions_list

    @staticmethod
    def get_alternative_paths(path: List[bool]) -> List[List[bool]]:
        paths = [list(p) for p in itertools.product((True, False), repeat=len(path))]
        paths.remove(path)
        return paths
