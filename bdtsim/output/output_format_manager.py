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

from typing import Any, Dict, Type

from .output_format import OutputFormat


class OutputFormatRegistration(object):
    def __init__(self, cls: Type[OutputFormat], *args: Any, **kwargs: Any) -> None:
        self.cls = cls
        self.args = args
        self.kwargs = kwargs


class OutputFormatManager(object):
    output_formats: Dict[str, OutputFormatRegistration] = {}

    def __init__(self) -> None:
        raise NotImplementedError('This class is not to be instantiated')

    @staticmethod
    def register(name: str, cls: Type[OutputFormat], *args: Any, **kwargs: Any) -> None:
        if not issubclass(cls, OutputFormat):
            raise ValueError('Provided class is not a subclass of DataProvider')
        OutputFormatManager.output_formats[name] = OutputFormatRegistration(cls, *args, **kwargs)

    @staticmethod
    def instantiate(name: str, **kwargs: Any) -> OutputFormat:
        output_format = OutputFormatManager.output_formats[name]
        return output_format.cls(*output_format.args, **{**output_format.kwargs, **kwargs})
