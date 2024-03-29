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

from typing import Any, BinaryIO


class DataProvider(object):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize DataProvider

        Args:
            *args (Any): Collector for unrecognized positional arguments
            **kwargs (Any): Collector for unrecognized keyword arguments
        """
        if len(args):
            raise TypeError('Unrecognized positional argument "%s" for DataProvider' % str(args[0]))
        if len(kwargs):
            raise TypeError('Unrecognized keyword argument "%s" for DataProvider' % str(list(kwargs.keys())[0]))

    @property
    def data_size(self) -> int:
        raise NotImplementedError()

    @property
    def file_pointer(self) -> BinaryIO:
        raise NotImplementedError()
