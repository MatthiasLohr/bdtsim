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

from typing import Any, Dict, Generic, Optional, TypeVar, cast

from .account import Account


T = TypeVar('T', float, int)


class AccountRelatedNumericalCollection(Dict[Account, T], Generic[T]):
    def __init__(self, init: Optional[Dict[Account, T]] = None) -> None:
        super(AccountRelatedNumericalCollection, self).__init__()
        if init is not None:
            for k, v in init.items():
                self.update({k: v})

    def get(self, account: Account, default: T = 0) -> T:  # type: ignore
        return cast(T, super().get(account, default))

    @property
    def is_neutral(self) -> bool:
        for amount in self.values():
            if not amount == 0:
                return False
        return True

    def __repr__(self) -> str:
        return '<%s.%s %s>' % (
            __name__,
            FundsDiffCollection.__name__,
            ', '.join(['%s: %d' % (account.name, diff) for account, diff in self.items()])
        )

    def __iadd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for account, other_amount in other.items():
                current_amount = self.get(account)
                if current_amount is None:
                    self.update({account: other_amount})
                else:
                    self.update({account: current_amount + other_amount})
            return self
        else:
            return NotImplemented

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            result = self.__class__()
            result += self
            result += other
            return result
        else:
            return NotImplemented

    def __isub__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for account, other_amount in other.items():
                current_amount = self.get(account)
                if current_amount is None:
                    self.update({account: -other_amount})
                else:
                    self.update({account: current_amount - other_amount})
            return self
        else:
            return NotImplemented

    def __sub__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            result = self.__class__()
            result += self
            result -= other
            return result
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            for a, b in (self, other), (other, self):
                for account in a.keys():
                    if a.get(account) != b.get(account):
                        return False
            return True
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class FundsDiffCollection(AccountRelatedNumericalCollection[int]):
    pass


class ItemShareCollection(AccountRelatedNumericalCollection[float]):
    pass
