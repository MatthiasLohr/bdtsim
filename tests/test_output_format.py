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

import unittest

from bdtsim.output import OutputFormat


class OutputFormatTest(unittest.TestCase):
    def test_wei_scaling(self) -> None:
        self.assertEqual(OutputFormat.scale_wei_static(1, 1), 1)
        self.assertEqual(OutputFormat.scale_wei_static(10, 0.1), 1)
        self.assertEqual(OutputFormat.scale_wei_static(300, 0.01), 3)

        self.assertEqual(OutputFormat.scale_wei_static(1, 'Wei'), 1)
        self.assertEqual(OutputFormat.scale_wei_static(42000000000, 'Gwei'), 42)

        self.assertEqual(OutputFormat.scale_wei_static(19000000000000000000, 'Eth'), 19)

    def test_gas_scaling(self) -> None:
        self.assertEqual(OutputFormat.scale_gas_static(1, 1), 1)
        self.assertEqual(OutputFormat.scale_gas_static(10, 0.1), 1)
        self.assertEqual(OutputFormat.scale_gas_static(300, 0.01), 3)

    def test_get_unit_factor(self) -> None:
        self.assertEqual(OutputFormat.get_unit_factor(''), 1)
        self.assertEqual(OutputFormat.get_unit_factor('k'), 1000)

        self.assertRaises(ValueError, OutputFormat.get_unit_factor, 'Q')
