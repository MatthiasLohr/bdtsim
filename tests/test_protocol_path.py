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
from bdtsim.participant import seller, buyer
from bdtsim.protocol_path import Decision, ProtocolPath


class DecisionTest(unittest.TestCase):
    def test_equals(self):
        self.assertEqual(Decision(True, seller), Decision(True, seller))
        self.assertEqual(Decision(False, seller), Decision(False, seller))

        self.assertNotEqual(Decision(True, seller), Decision(True, buyer))
        self.assertNotEqual(Decision(False, seller), Decision(False, buyer))
        self.assertNotEqual(Decision(True, seller), Decision(False, seller))
        self.assertNotEqual(Decision(False, seller), Decision(True, seller))


class ProtocolPathTest(unittest.TestCase):
    def test_get_alternatives(self):
        test_path = ProtocolPath()
        test_path.decide(seller)
        self.assertEqual([
            ProtocolPath([Decision(False, seller)])
        ], test_path.get_alternatives())

        test_path.decide(buyer)
        self.assertEqual([
            ProtocolPath([Decision(False, seller)]),
            ProtocolPath([Decision(True, seller), Decision(False, buyer)])
        ], test_path.get_alternatives())
