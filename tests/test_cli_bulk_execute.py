# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2021 Matthias Lohr <mail@mlohr.com>
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

from unittest import TestCase

from bdtsim.cli.bulk_execute import BulkExecuteSubCommand


class BulkExecuteSubCommandTest(TestCase):
    def test_get_output_filename(self) -> None:
        self.assertEqual(
            'FairSwap-size=256_PyEVM_RandomDataProvider.result',
            BulkExecuteSubCommand.get_output_filename(
                simulation_configuration={
                    'protocol': {
                        'name': 'FairSwap',
                        'parameters': {
                            'size': 256
                        }
                    },
                    'environment': {
                        'name': 'PyEVM'
                    }
                },
                renderer_configuration=None,
                suffix='result'
            )
        )
