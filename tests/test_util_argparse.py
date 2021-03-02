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

from bdtsim.util.argparse import ProtocolPathCoercionParameter


class ProtocolPathCoercionParameterTest(unittest.TestCase):
    def test_value(self) -> None:
        parser = ProtocolPathCoercionParameter()

        coercion = parser(None)
        self.assertEqual(coercion, [])

        coercion = parser('outcome1')
        self.assertEqual(coercion, [['outcome1']])

        coercion = parser('outcome1,outcome2,outcome3')
        self.assertEqual(coercion, [['outcome1'], ['outcome2'], ['outcome3']])

        coercion = parser('outcome1|outcome2,*,outcome3')
        self.assertEqual(coercion, [['outcome1', 'outcome2'], None, ['outcome3']])
