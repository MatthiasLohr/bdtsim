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

from bdtsim.simulation_result import SimulationResult
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager


class HumanReadableOutputFormat(OutputFormat):
    def __init__(self) -> None:
        super(HumanReadableOutputFormat, self).__init__()

    def render(self, simulation_result: SimulationResult) -> None:
        if len(simulation_result.preparation_transactions.aggregation) > 0:
            print('Preparation Results:')
            for preparation_entry in simulation_result.preparation_transactions.aggregation.values():
                print('  %s' % str(preparation_entry))

        print('Execution Results:')
        for description, aggregation in simulation_result.get_important_execution_results():
            print('  %s' % description)
            for execution_entry in aggregation.values():
                print('    %s' % str(execution_entry))

        if len(simulation_result.cleanup_transactions.aggregation) > 0:
            print('Cleanup Results:')
            for cleanup_entry in simulation_result.cleanup_transactions.aggregation.values():
                print('  %s' % str(cleanup_entry))


OutputFormatManager.register('human-readable', HumanReadableOutputFormat)
