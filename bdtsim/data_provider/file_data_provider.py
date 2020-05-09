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

from typing import BinaryIO, Optional

from .data_provider import DataProvider
from .data_provider_manager import DataProviderManager


class FileDataProvider(DataProvider):
    def __init__(self, filename: str) -> None:
        super(FileDataProvider, self).__init__()
        self._filename = filename
        self._fp: Optional[BinaryIO] = None

    @property
    def data_size(self) -> int:
        current = self.file_pointer.tell()  # save current position
        self.file_pointer.seek(0, 2)  # seek to the end of the file
        size = self.file_pointer.tell()  # save current position (size)
        self.file_pointer.seek(current, 0)  # move to previous position
        return size

    @property
    def file_pointer(self) -> BinaryIO:
        if self._fp is None:
            self._fp = open(self._filename, 'rb')
        return self._fp

    def __del__(self) -> None:
        if self._fp is not None:
            self._fp.close()
            self._fp = None


DataProviderManager.register('FileDataProvider', FileDataProvider)
