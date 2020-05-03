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

import time
from typing import Any, List, Optional

from .participant import Participant


class Decision(object):
    def __init__(self, decision: bool, account: Participant, timestamp: Optional[float] = None) -> None:
        self._decision = decision
        self._account = account
        self._timestamp = timestamp

    @property
    def decision(self) -> bool:
        return self._decision

    @property
    def account(self) -> Participant:
        return self._account

    @property
    def timestamp(self) -> Optional[float]:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: float) -> None:
        self._timestamp = timestamp

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Decision) and other.decision == self.decision and other.account == self.account

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return '<%s.%s %s, account: %s>' % (__name__, self.__class__.__name__, str(self.decision), repr(self.account))

    def __str__(self) -> str:
        tmp = 'Y' if self.decision else 'N'
        if self.account is not None:
            tmp += '/' + self.account.name
        return tmp


class ProtocolPath(object):
    def __init__(self, decisions_list: Optional[List[Decision]] = None):
        self._initial_decisions_list: List[Decision] = decisions_list or []
        self._new_decisions_list: List[Decision] = []
        self._decisions_index: int = 0

    def decide(self, account: Participant) -> bool:
        if len(self.decisions_list) == self._decisions_index:
            self._new_decisions_list.append(Decision(True, account, None))
        decision = self.decisions_list[self._decisions_index]
        decision.timestamp = time.time()
        if decision.account != account:
            raise ValueError('Predefined decision is not originating from current decider')
        self._decisions_index += 1
        return decision.decision

    @property
    def initial_decisions_list(self) -> List[Decision]:
        return self._initial_decisions_list

    @property
    def new_decisions_list(self) -> List[Decision]:
        return self._new_decisions_list

    @property
    def decisions_list(self) -> List[Decision]:
        return self.initial_decisions_list + self.new_decisions_list

    def get_alternatives(self) -> List['ProtocolPath']:
        alternatives = []
        for i in range(len(self._new_decisions_list)):
            head = self._new_decisions_list[i]
            alternatives.append(ProtocolPath(
                self._new_decisions_list[:i] + [Decision(not head.decision, head.account)]
            ))
        return alternatives

    @property
    def is_completely_honest(self) -> bool:
        for d in self.decisions_list:
            if not d.decision:
                return False
        return True

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, ProtocolPath) and
                self._initial_decisions_list == other._initial_decisions_list and
                self._new_decisions_list == other._new_decisions_list)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        str_initial = map(lambda d: str(d), self._initial_decisions_list)
        str_new = map(lambda d: str(d), self._new_decisions_list)
        return '<%s.%s: [%s]+[%s]>' % (
            __name__,
            ProtocolPath.__name__,
            ', '.join(str_initial),
            ', '.join(str_new),
        )
