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
    def test_init(self):
        # should pass:
        Decision(seller, 1, 2)

        self.assertRaises(ValueError, Decision, seller, 1, 1)
        self.assertRaises(ValueError, Decision, seller, 2, 1)
        self.assertRaises(ValueError, Decision, seller, -1, -2)

    def test_equals(self):
        self.assertEqual(1, Decision(seller, 1, 3))
        self.assertEqual(Decision(seller, 1, 3), 1)
        self.assertEqual(Decision(seller, 1, 3), Decision(seller, 1, 3))

        self.assertNotEqual(Decision(seller, 1, 3), Decision(buyer, 1, 3))
        self.assertNotEqual(Decision(seller, 1, 3), Decision(seller, 2, 3))
        self.assertNotEqual(Decision(seller, 1, 3), Decision(seller, 1, 4))


class ProtocolPathTest(unittest.TestCase):
    def test_get_alternatives2(self):
        path = ProtocolPath()
        path.decide(seller)
        self.assertEqual([
            ProtocolPath([Decision(seller, 2)])
        ], path.get_alternatives())

        path.decide(buyer)
        self.assertEqual([
            ProtocolPath([Decision(seller, 2)]),
            ProtocolPath([Decision(seller, 1), Decision(buyer, 2)])
        ], path.get_alternatives())

    def test_get_alternatives3(self):
        path = ProtocolPath()
        path.decide(seller, 3)
        self.assertEqual([
            ProtocolPath([Decision(seller, 2, 3)]),
            ProtocolPath([Decision(seller, 3, 3)])
        ], path.get_alternatives())

        path.decide(buyer, 3)
        self.assertEqual([
            ProtocolPath([Decision(seller, 2, 3)]),
            ProtocolPath([Decision(seller, 3, 3)]),
            ProtocolPath([Decision(seller, 1, 3), Decision(buyer, 2, 3)]),
            ProtocolPath([Decision(seller, 1, 3), Decision(buyer, 3, 3)])
        ], path.get_alternatives())
