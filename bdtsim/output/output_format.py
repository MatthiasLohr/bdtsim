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

from typing import Any, Optional, Union

from .simulation_result import SimulationResult


class OutputFormat(object):
    def __init__(self, wei_scaling: Union[int, float, str] = 1, gas_scaling: Union[int, float, str] = 1,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize OutputFormat

        Args:
            wei_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed as well as
                Ethereum unit prefixes (Wei, GWei, Eth).
            gas_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed.
            *args (Any): Collector for unrecognized positional arguments
            **kwargs (Any): Collector for unrecognized keyword arguments
        """
        if len(args):
            raise TypeError('Unrecognized positional argument "%s" for OutputFormat' % str(args[0]))
        if len(kwargs):
            raise TypeError('Unrecognized keyword argument "%s" for OutputFormat' % str(list(kwargs.keys())[0]))

        self._wei_scaling = wei_scaling
        self._gas_scaling = gas_scaling

    def render(self, simulation_result: SimulationResult) -> None:
        raise NotImplementedError()

    def scale_wei(self, value: int, scaling: Optional[Union[int, float, str]]) -> Union[float, int]:
        if scaling is not None:
            return self.scale_wei_static(value, scaling)
        else:
            return self.scale_wei_static(value, self._wei_scaling)

    def scale_gas(self, value: int, scaling: Optional[Union[int, float, str]]) -> Union[float, int]:
        if scaling is not None:
            return self.scale_gas_static(value, scaling)
        else:
            return self.scale_gas_static(value, self._gas_scaling)

    @staticmethod
    def scale_wei_static(value: int, scaling: Union[int, float, str]) -> Union[float, int]:
        if isinstance(scaling, int) or isinstance(scaling, float):
            factor = 1 / scaling
        elif isinstance(scaling, str):
            # filter Ethereum units
            factor = 1
            if scaling.lower().endswith('wei'):
                scaling = scaling[:-3]
            elif scaling.lower().endswith('eth'):
                factor = 1000000000000000000
                scaling = scaling[:-3]
            # filter common units
            factor = factor * OutputFormat.get_unit_factor(scaling)
        else:
            raise ValueError('Unsupported scaling type')
        result = value / factor
        if result.is_integer():
            return int(result)
        else:
            return result

    @staticmethod
    def scale_gas_static(value: int, scaling: Union[int, float, str]) -> Union[float, int]:
        if isinstance(scaling, int) or isinstance(scaling, float):
            factor = 1 / scaling
        elif isinstance(scaling, str):
            # filter common units
            factor = OutputFormat.get_unit_factor(scaling)
        else:
            raise ValueError('Unsupported scaling type')
        result = value / factor
        if result.is_integer():
            return int(result)
        else:
            return result

    @staticmethod
    def get_unit_factor(unit: str) -> Union[float, int]:
        if unit == '':
            return 1

        units = {
            'p': 0.000000000001,  # pico
            'n': 0.000000001,     # nano
            'μ': 0.000001,        # micro
            'm': 0.001,
            'k': 1000,
            'M': 1000000,
            'G': 1000000000,
            'T': 1000000000000,
            'P': 1000000000000000,
            'E': 1000000000000000000,
            'Z': 1000000000000000000000,
            'Y': 1000000000000000000000000,
        }

        factor = units.get(unit)
        if factor is None:
            raise ValueError('Unsupported unit!')

        return factor
