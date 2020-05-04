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
    HONEST_VARIANTS_DEFAULT = [1]
    """A single decision within a `ProtocolPath`.

    Decisions are represented by integers (starting with 1).
    By convention, 1 means "honest"/"most honest" decision, all other values (2, 3, ...) represent a dishonest/cheating
    decision.
    """

    def __init__(self, account: Participant, variant: int, variants: int = 2,
                 timestamp: Optional[float] = None, description: Optional[str] = None) -> None:
        """
        Args:
            account (Participant): Who is deciding about the next step
            variant (int): Variant chosen in this decision
            variants (int): Number of variants possible for this decision
            description (str): Description of this decision variant (not considered for equality)
        """
        if variants < 2:
            raise ValueError('Only two or more variants are possible')
        if variant < 1 or variant > variants:
            raise ValueError('Only %d variants allowed, variant %d not supported' % (variants, variant))

        self._account = account
        self._variant = variant
        self._variants = variants
        self._timestamp = timestamp
        self._description = description

    @property
    def account(self) -> Participant:
        return self._account

    @property
    def variant(self) -> int:
        return self._variant

    @property
    def variants(self) -> int:
        return self._variants

    @property
    def timestamp(self) -> Optional[float]:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: float) -> None:
        self._timestamp = timestamp

    @property
    def description(self) -> Optional[str]:
        return self._description

    def is_honest(self, honest_variants: Optional[List[int]] = None) -> bool:
        if honest_variants is None:
            honest_variants = self.HONEST_VARIANTS_DEFAULT
        return self.variant in honest_variants

    def is_variant(self, variant: int) -> bool:
        return self.variant == variant

    def __eq__(self, other: Any) -> bool:
        """Supports equality checks with other Decision instances and int(egers).

        When an int is provided, the int value is compared to the `variant` field.

        Args:
            other: (Decision, int): Object to compare to

        Returns:
            bool: Equality
        """
        if isinstance(other, Decision):
            return self.account == other.account and self.variant == other.variant and self.variants == other.variants
        elif isinstance(other, int):
            if other < 1:
                raise ValueError('Since we are comparing Decision variants only positive integers are allowed')
            return other == self.variant
        else:
            raise NotImplementedError()

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return '' % (

        )

    def __str__(self) -> str:
        return '%d/%d(%s)' % (
            self.variant,
            self.variants,
            self.account.name
        )


class ProtocolPath(object):
    """One possible path through a protocol iteration."""

    def __init__(self, initial_decisions: Optional[List[Decision]] = None) -> None:
        self._initial_decisions: List[Decision] = initial_decisions or []
        self._new_decisions: List[Decision] = []
        self._decisions_index: int = 0

    def decide(self, account: Participant, variants: int = 2, description: Optional[str] = None) -> Decision:
        if len(self.decisions) == self._decisions_index:
            # we have no decision yet, creating a new one
            self._new_decisions.append(Decision(
                account=account,
                variant=1,
                variants=variants,
                timestamp=time.time(),
                description=description
            ))

        decision = self.decisions[self._decisions_index]

        # if there is a pre-defined decision, set timestamp when it was used (now)
        if decision.timestamp is None:
            decision.timestamp = time.time()

        # do some decision validity checks
        if decision.account != account:
            raise ValueError('Account provided does not match pre-defined decision account %s' % str(decision.account))
        if decision.variants != variants:
            raise ValueError('Number of possible variants provided does not match pre-defined decision variants (%d)'
                             % decision.variants)

        self._decisions_index += 1
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

    def get_alternatives(self) -> List['ProtocolPath']:
        alternatives = []
        for new_decision_index in range(len(self.new_decisions)):
            decision_head = self.new_decisions[new_decision_index]
            for variant in range(1, decision_head.variants + 1):
                if decision_head.variant == variant:
                    continue
                alternatives.append(ProtocolPath(
                    self.initial_decisions + self.new_decisions[:new_decision_index] + [Decision(
                        account=decision_head.account,
                        variant=variant,
                        variants=decision_head.variants,
                        timestamp=None,
                        description=decision_head.description
                    )]
                ))
        return alternatives

    def all_participants_were_honest(self, honest_variants: Optional[List[int]] = None) -> bool:
        if honest_variants is None:
            honest_variants = Decision.HONEST_VARIANTS_DEFAULT
        for decision in self.decisions:
            if decision.variant not in honest_variants:
                return False
        return True

    def participant_was_honest(self, account: Participant, honest_variants: Optional[List[int]] = None) -> bool:
        if honest_variants is None:
            honest_variants = Decision.HONEST_VARIANTS_DEFAULT
        for decision in self.decisions:
            if decision.account != account:
                continue
            if decision.variant not in honest_variants:
                return False
        return True

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ProtocolPath):
            return self.initial_decisions == other.initial_decisions and self.new_decisions == other.new_decisions
        else:
            raise NotImplementedError()

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        initial_decisions_str = map(lambda d: str(d), self.initial_decisions)
        new_decisions_str = map(lambda d: str(d), self.new_decisions)
        return '<%s.%s: [%s]+[%s]>' % (
            __name__,
            ProtocolPath.__name__,
            ','.join(initial_decisions_str),
            ','.join(new_decisions_str),
        )
