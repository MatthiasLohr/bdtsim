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

from typing import Any, Dict, Optional

from .account import Account


class FundsDiffCollection(object):
    def __init__(self, initial: Optional[Dict[Account, int]] = None) -> None:
        if initial is not None:
            self._dict = initial
        else:
            self._dict = {}

    def get(self, account: Account) -> int:
        diff = self._dict.get(account)
        if diff is None:
            return 0
        else:
            return diff

    def __repr__(self) -> str:
        return '<%s.%s %s>' % (
            __name__,
            FundsDiffCollection.__name__,
            ', '.join(['%s: %d' % (account.name, diff) for account, diff in self._dict.items()])
        )

    def __iadd__(self, other: Any) -> 'FundsDiffCollection':
        if isinstance(other, FundsDiffCollection):
            for account, other_amount in other._dict.items():
                current_amount = self._dict.get(account)
                if current_amount is None:
                    self._dict.update({account: other_amount})
                else:
                    self._dict.update({account: current_amount + other_amount})
            return self
        else:
            return NotImplemented

    def __isub__(self, other: Any) -> 'FundsDiffCollection':
        if isinstance(other, FundsDiffCollection):
            for account, other_amount in other._dict.items():
                current_amount = self._dict.get(account)
                if current_amount is None:
                    self._dict.update({account: -other_amount})
                else:
                    self._dict.update({account: current_amount - other_amount})
            return self
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FundsDiffCollection):
            for a, b in (self._dict, other._dict), (other._dict, self._dict):
                for account in a.keys():
                    if a.get(account, 0) != b.get(account, 0):
                        return False
            return True
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
