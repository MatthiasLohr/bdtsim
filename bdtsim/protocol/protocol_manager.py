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

from .protocol import Protocol


class ProtocolManager(object):
    protocols = {}

    def __init__(self):
        raise NotImplementedError('This class is not to be instantiated')

    @staticmethod
    def register(name, cls, *args, **kwargs):
        if not issubclass(cls, Protocol):
            raise ValueError('Provided class is not a subclass of Protocol')
        ProtocolManager.protocols[name] = {
            'cls': cls,
            'args': args,
            'kwargs': kwargs
        }

    @staticmethod
    def instantiate(name, **kwargs):
        environment = ProtocolManager.protocols[name]
        return environment['cls'](*environment['args'], **{**environment['kwargs'], **kwargs})