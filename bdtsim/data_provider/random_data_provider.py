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

import random
from io import BytesIO
from typing import BinaryIO, Optional

from .data_provider import DataProvider
from .data_provider_manager import DataProviderManager


class RandomDataProvider(DataProvider):
    def __init__(self, size: int = 1048576, seed: int = 42) -> None:
        super(RandomDataProvider, self).__init__()
        self._size = int(size)
        self._seed = seed
        self._mem_file: Optional[BytesIO] = None

    @property
    def data_size(self) -> int:
        return self._size

    @property
    def file_pointer(self) -> BinaryIO:
        if self._mem_file is None:
            random.seed(self._seed)
            self._mem_file = BytesIO(bytearray(random.getrandbits(8) for _ in range(self._size)))
        return self._mem_file


DataProviderManager.register('RandomDataProvider', RandomDataProvider)
