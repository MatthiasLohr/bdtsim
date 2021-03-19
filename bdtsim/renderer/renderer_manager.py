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

from .renderer import Renderer


class RendererRegistration(object):
    def __init__(self, cls: Type[Renderer], *args: Any, **kwargs: Any) -> None:
        self.cls = cls
        self.args = args
        self.kwargs = kwargs


class RendererManager(object):
    renderers: Dict[str, RendererRegistration] = {}

    def __init__(self) -> None:
        raise NotImplementedError('This class is not to be instantiated')

    @staticmethod
    def register(name: str, cls: Type[Renderer], *args: Any, **kwargs: Any) -> None:
        if not issubclass(cls, Renderer):
            raise ValueError('Provided class is not a subclass of DataProvider')
        RendererManager.renderers[name] = RendererRegistration(cls, *args, **kwargs)

    @staticmethod
    def instantiate(name: str, **kwargs: Any) -> Renderer:
        renderer = RendererManager.renderers[name]
        return renderer.cls(*renderer.args, **{**renderer.kwargs, **kwargs})
