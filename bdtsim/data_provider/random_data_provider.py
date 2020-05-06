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

import io

from .data_provider import DataProvider
from .data_provider_manager import DataProviderManager


class RandomDataProvider(DataProvider):
    def __init__(self, size: int = 1000000, seed: int = 42) -> None:
        super(RandomDataProvider, self).__init__()
        self._size = size
        # TODO implement


DataProviderManager.register('RandomDataProvider', RandomDataProvider)
