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

import json
import yaml

from .json import JSONEncoder
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager
from .simulation_result import SimulationResult


class YAMLOutputFormat(OutputFormat):
    def __init__(self) -> None:
        super(YAMLOutputFormat, self).__init__()

    def render(self, simulation_result: SimulationResult) -> None:
        json_str = json.dumps(simulation_result, cls=JSONEncoder)
        print(yaml.dump(json.loads(json_str)))


OutputFormatManager.register('yaml', YAMLOutputFormat)
