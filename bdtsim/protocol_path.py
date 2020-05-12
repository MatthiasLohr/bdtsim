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
from typing import Any, Callable, List, Optional

from .account import Account


class Decision(object):
    """A single decision within a `ProtocolPath`.

    Decisions are represented by integers (starting with 1).
    By convention, 1 means "honest"/"most honest" decision, all other values (2, 3, ...) represent a dishonest/cheating
    decision.
    """

    def __init__(self, account: Account, variant: str, variants: List[str], honest_variants: Optional[List[str]] = None,
                 description: Optional[str] = None, timestamp: Optional[float] = None) -> None:
        """
        Args:
            account (Account): Who is deciding about the next step
            variant (str): Variant chosen in this decision
            variants (List[str]): Possible variants
            honest_variants (List[str]): List of variants to be considered as honest
            description (str): Description of this decision variant (not considered for equality)
            timestamp (float): When the decision has taken place
        """
        if len(variants) < 2:
            raise ValueError('You have to provide at least 2 variants for a decision')
        if variant not in variants:
            raise ValueError('%s not in list of possible variants (%s)' % (variant, ', '.join(variants)))
        if honest_variants is not None:
            for honest_variant in honest_variants:
                if honest_variant not in variants:
                    raise ValueError('Honest variants have to be part of possible variants list')

        self._account = account
        self._variant = variant
        self._variants = variants
        self._honest_variants: List[str] = honest_variants or [variants[0]]
        self._timestamp = timestamp
        self._description = description

    @property
    def account(self) -> Account:
        return self._account

    @property
    def variant(self) -> str:
        return self._variant

    @property
    def variants(self) -> List[str]:
        return self._variants

    @property
    def honest_variants(self) -> List[str]:
        return self._honest_variants

    @property
    def timestamp(self) -> Optional[float]:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: float) -> None:
        self._timestamp = timestamp

    @property
    def description(self) -> Optional[str]:
        return self._description

    def is_honest(self) -> bool:
        return self.variant in self._honest_variants

    def is_variant(self, variant: str) -> bool:
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
            return (self.account == other.account
                    and self.variant == other.variant
                    and self.variants == other.variants
                    and self._honest_variants == other._honest_variants)
        elif isinstance(other, str):
            if other not in self.variants:
                raise ValueError('%s is not an allowed variant (%s)' % (other, ', '.join(self.variants)))
            return other == self.variant
        else:
            raise NotImplementedError()

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self._account, self._variant, tuple(self._variants)))

    def __repr__(self) -> str:
        return '<%s.%s by %s: %s (%s)>' % (
            __name__,
            Decision.__name__,
            self.account.name,
            self.variant,
            ', '.join(self.variants)
        )

    def __str__(self) -> str:
        return '%s: %s (%s)' % (
            self.account.name,
            self.variant,
            ', '.join(self.variants)
        )


class ProtocolPath(object):
    """One possible path through a protocol iteration."""

    def __init__(self, initial_decisions: Optional[List[Decision]] = None) -> None:
        self._initial_decisions: List[Decision] = initial_decisions or []
        self._new_decisions: List[Decision] = []
        self._decisions_index: int = 0
        self._decision_callback: Optional[Callable[[Decision], None]] = None

    def decide(self, account: Account, description: str, variants: List[str]) -> Decision:
        if len(self.decisions) == self._decisions_index:
            # we have no decision yet, creating a new one
            self._new_decisions.append(Decision(
                account=account,
                variant=variants[0],
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
            for variant in decision_head.variants:
                if decision_head.variant == variant:
                    continue
                alternatives.append(ProtocolPath(
                    self.initial_decisions + self.new_decisions[:new_decision_index] + [Decision(
                        account=decision_head.account,
                        variant=variant,
                        variants=decision_head.variants,
                        honest_variants=decision_head._honest_variants,
                        timestamp=None,
                        description=decision_head.description
                    )]
                ))
        return alternatives

    def all_participants_were_honest(self, honest_variants: Optional[List[str]] = None) -> bool:
        if honest_variants is None:
            for decision in self.decisions:
                if decision.variants.index(decision.variant) > 0:
                    return False
            return True
        else:
            for decision in self.decisions:
                if decision.variant not in honest_variants:
                    return False
            return True

    def participant_was_honest(self, account: Account, honest_variants: Optional[List[str]] = None) -> bool:
        if honest_variants is None:
            for decision in self.decisions:
                if decision.account != account:
                    continue
                if decision.variants.index(decision.variant) > 0:
                    return False
            return True
        else:
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
            ', '.join(initial_decisions_str),
            ', '.join(new_decisions_str),
        )
