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

import math
from typing import Any, Optional


class FileSize(object):
    SUFFIXES = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

    def __init__(self, value: Any) -> None:
        self._size = self.parse_value(value)

    @staticmethod
    def parse_value(value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            suffix = value[-1:].lower()
            suffix_index = None
            for i, s in enumerate(FileSize.SUFFIXES):
                if s.lower() == suffix:
                    suffix_index = i
                    break

            if suffix_index is None:
                return int(value)
            else:
                return int(float(value[:-1]) * (1000 ** (suffix_index + 1)))
        else:
            raise ValueError('Unsupported type: %s' % type(value))

    @staticmethod
    def format_human_readable(b: int, ndigits: Optional[int] = None) -> str:
        log = math.log(b, 1000)
        if log >= 1:
            exp = math.floor(log)
            return str(round(b / 1000 ** exp, ndigits)) + FileSize.SUFFIXES[exp - 1]
        else:
            return str(b)

    def human_readable(self) -> str:
        return self.format_human_readable(self._size)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FileSize):
            return self._size == other._size
        elif isinstance(other, int):
            return self._size == other
        elif isinstance(other, str):
            return self._size == FileSize(other)._size
        else:
            raise NotImplementedError()

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return '<%s.%s %d bytes (%s)>' % (
            __name__,
            FileSize.__name__,
            self._size,
            self.format_human_readable(self._size)
        )

    def __str__(self) -> str:
        return '<%s %d bytes (%s)>' % (
            FileSize.__name__,
            self._size,
            self.format_human_readable(self._size)
        )
