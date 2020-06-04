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

from bdtsim.util.types import to_bool


class TypeUtilTest(unittest.TestCase):
    def test_to_bool(self):
        self.assertEqual(True, to_bool(True))
        self.assertEqual(True, to_bool('True'))
        self.assertEqual(True, to_bool('true'))
        self.assertEqual(True, to_bool('Yes'))
        self.assertEqual(True, to_bool('yes'))
        self.assertEqual(True, to_bool('Y'))
        self.assertEqual(True, to_bool('y'))
        self.assertEqual(True, to_bool('1'))

        self.assertEqual(False, to_bool(False))
        self.assertEqual(False, to_bool('False'))
        self.assertEqual(False, to_bool('false'))
        self.assertEqual(False, to_bool('No'))
        self.assertEqual(False, to_bool('no'))
        self.assertEqual(False, to_bool('N'))
        self.assertEqual(False, to_bool('n'))
        self.assertEqual(False, to_bool('0'))

        self.assertRaises(ValueError, to_bool, 'foobar')
