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
from typing import Any, Callable, List, Optional, Tuple, cast

from .account import Account


class Choice(object):
    """A choice for making decisions when executing a protocol"""
    def __init__(self, subject: Account, options: Tuple[str, ...], honest_options: Optional[Tuple[str, ...]] = None,
                 description: Optional[str] = None) -> None:
        """
        Args:
            subject (Account): Subject which is eligible to make a decision.
            options (List[str]): Available options for the decision.
            honest_options (List[str]): Subset of variants which are considered to be honest. Defaults to the first
                provided option.
            description (str): Description of the decision to be made.
        """
        if len(options) < 2:
            raise ValueError('a choice needs to have at least two options')
        if honest_options is not None:
            for honest_option in honest_options:
                if honest_option not in options:
                    raise ValueError('all options defined to be honest must be allowed by the choice')

        self._subject = subject
        self._options = options
        self._honest_options = honest_options or (options[0], )
        self._description = description

    @property
    def subject(self) -> Account:
        return self._subject

    @property
    def options(self) -> Tuple[str, ...]:
        return self._options

    @property
    def honest_options(self) -> Tuple[str, ...]:
        return self._honest_options

    @property
    def description(self) -> Optional[str]:
        return self._description

    def choose(self, outcome: str, timestamp: Optional[float] = None) -> 'Decision':
        if outcome not in self._options:
            raise ValueError('desired outcome "%s" is not a valid option. Choose between: %s' % (
                outcome,
                ', '.join(self._options)
            ))

        return Decision(
            choice=self,
            outcome=outcome,
            timestamp=timestamp
        )

    def __repr__(self) -> str:
        return str({
            'subject': self._subject,
            'options': self._options,
            'honest_options': self._honest_options,
            'description': self._description
        })


class Decision(object):
    def __init__(self, choice: Choice, outcome: str, timestamp: Optional[float] = None):
        if outcome not in choice.options:
            raise ValueError('the outcome provided is not allowed by the choice')

        self._choice = choice
        self._outcome = outcome
        self._timestamp = timestamp

    @property
    def choice(self) -> Choice:
        return self._choice

    @property
    def outcome(self) -> str:
        return self._outcome

    @property
    def timestamp(self) -> Optional[float]:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: Optional[float]) -> None:
        self._timestamp = timestamp

    def is_honest(self) -> bool:
        return self._outcome in self.choice.honest_options

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Decision):
            return self._choice == other._choice and self._outcome == other._outcome
        elif isinstance(other, str):
            return self._outcome == other
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self._choice, self._outcome))

    def __str__(self) -> str:
        str_parts = []
        for option in self._choice.options:
            str_part = option

            if str_part in self._choice.honest_options:
                str_part += '+'
            else:
                str_part += '-'

            if option == self._outcome:
                str_part = '>' + str_part + '<'
            str_parts.append(str_part)

        return '<Decision "%s": %s>' % (
            self._choice.description,
            ', '.join(str_parts)
        )

    def __repr__(self) -> str:
        return str({
            'outcome': self._outcome,
            'choice': repr(self._choice)
        })


class ProtocolPathCoercion(List[Optional[List[str]]]):
    pass


class ProtocolPath(object):
    """One possible path through a protocol iteration."""

    def __init__(self, initial_decisions: Optional[List[Decision]] = None,
                 coercion: Optional[ProtocolPathCoercion] = None) -> None:
        self._initial_decisions: List[Decision] = initial_decisions or []
        self._coercion: ProtocolPathCoercion = coercion or ProtocolPathCoercion()
        self._new_decisions: List[Decision] = []
        self._decisions_index: int = 0
        self._decision_callback: Optional[Callable[[Decision], None]] = None

    def decide(self, subject: Account, description: str, options: Tuple[str, ...],
               honest_options: Optional[Tuple[str, ...]] = None) -> Decision:
        if len(self.decisions) == self._decisions_index:  # we have no decision yet
            # check for outcome coercion
            outcome: Optional[str] = None
            if len(self._coercion) <= self._decisions_index or self._coercion[self._decisions_index] is None:
                outcome = options[0]
            else:
                for variant in options:
                    if variant in cast('List[str]', self._coercion[self._decisions_index]):
                        outcome = variant
                        break
                if outcome is None:
                    raise RuntimeError('No accepted outcome available. Choose from: %s' % ', '.join(options))

            # create decision object
            self._new_decisions.append(Decision(
                choice=Choice(
                    subject=subject,
                    options=options,
                    honest_options=honest_options,
                    description=description
                ),
                outcome=outcome,
                timestamp=time.time()
            ))

        decision = self.decisions[self._decisions_index]

        if decision.choice.subject != subject:
            raise ValueError('subject should match existing decisions\'s subject')
        if decision.choice.options != options:
            raise ValueError('options should match existing decisions\'s options')
        if decision.choice.honest_options != (honest_options or (options[0], )):
            raise ValueError('honest options should match existing decisions\'s honest options')
        if decision.choice.description != description:
            raise ValueError('description should match existing decisions\'s description')

        # if there is a pre-defined decision, set timestamp when it was used (now)
        if decision.timestamp is None:
            decision.timestamp = time.time()

        # do some decision validity checks
        if decision.choice.subject != subject:
            raise ValueError('Account provided does not match pre-defined decision account %s'
                             % str(decision.choice.subject))
        if decision.choice.options != options:
            raise ValueError('Possible variants do not match')

        self._decisions_index += 1
        if self._decision_callback is not None:
            self._decision_callback(decision)
        return decision

    @property
    def initial_decisions(self) -> List[Decision]:
        return self._initial_decisions

    @property
    def new_decisions(self) -> List[Decision]:
        return self._new_decisions

    @property
    def decisions(self) -> List[Decision]:
        return self.initial_decisions + self.new_decisions

    @property
    def decision_callback(self) -> Optional[Callable[[Decision], None]]:
        return self._decision_callback

    @decision_callback.setter
    def decision_callback(self, callback: Optional[Callable[[Decision], None]]) -> None:
        self._decision_callback = callback

    def get_alternatives(self) -> List['ProtocolPath']:
        alternatives = []
        for new_decision_index in range(len(self.new_decisions)):
            decision_head = self.new_decisions[new_decision_index]
            for option in decision_head.choice.options:
                # filter current option
                if decision_head.outcome == option:
                    continue
                # filter coercions
                if (len(self._coercion) > new_decision_index
                        and self._coercion[new_decision_index] is not None
                        and option not in cast('List[str]', self._coercion[new_decision_index])):
                    continue
                # add alternative protocol path
                alternatives.append(ProtocolPath(
                    self.initial_decisions + self.new_decisions[:new_decision_index] + [Decision(
                        choice=decision_head.choice,
                        outcome=option,
                        timestamp=None
                    )]
                ))
        return alternatives

    def all_accounts_completely_honest(self) -> bool:
        for decision in self.decisions:
            if not decision.is_honest():
                return False
        return True

    def subject_completely_honest(self, subject: Account) -> bool:
        for decision in self.decisions:
            if decision.choice.subject != subject:
                continue
            if not decision.is_honest():
                return False
        return True

    @property
    def coercion_str(self) -> str:
        return ','.join([d.outcome for d in self.decisions])

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ProtocolPath):
            return self.initial_decisions == other.initial_decisions and self.new_decisions == other.new_decisions
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        initial_decisions_str = map(lambda d: str(d), self.initial_decisions)
        new_decisions_str = map(lambda d: str(d), self.new_decisions)
        return '<%s.%s: [%s]+[%s]>' % (
            __name__,
            ProtocolPath.__name__,
            ', '.join(initial_decisions_str),
            ', '.join(new_decisions_str),
        )
