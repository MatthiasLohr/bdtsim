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

from typing import Optional

from bdtsim.protocol_path import ProtocolPathCoercion


class ProtocolPathCoercionParameter(object):
    def __init__(self) -> None:
        pass

    def __call__(self, value: Optional[str]) -> ProtocolPathCoercion:
        coercion = ProtocolPathCoercion()
        if value is None:
            return coercion
        for decision in value.split(','):
            if decision == '*':
                coercion.append(None)
            else:
                coercion.append(list(decision.split('|')))
        return coercion
