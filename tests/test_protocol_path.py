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
from bdtsim.protocol_path import ProtocolPath, Decision


class DecisionTest(unittest.TestCase):
    def test_equals(self):
        self.assertEqual(Decision(True, seller), Decision(True, seller))
        self.assertEqual(Decision(False, seller), Decision(False, seller))

        self.assertNotEqual(Decision(True, seller), Decision(True, buyer))
        self.assertNotEqual(Decision(False, seller), Decision(False, buyer))
        self.assertNotEqual(Decision(True, seller), Decision(False, seller))
        self.assertNotEqual(Decision(False, seller), Decision(True, seller))


class ProtocolPathTest(unittest.TestCase):
    def test_get_alternative_decision_list(self):
        # two rounds with empty paths
        for protocol_path in ProtocolPath(), ProtocolPath([]):
            self.assertEqual(None, protocol_path.get_alternative_decision_list())

            result = protocol_path.decide(seller)
            self.assertEqual([Decision(not result, seller)], protocol_path.get_alternative_decision_list())

            protocol_path.decide(buyer)
            self.assertEqual([Decision(not result, seller)], protocol_path.get_alternative_decision_list())

        # new round with pre-defined path
        protocol_path = ProtocolPath([Decision(True, seller), Decision(False, buyer)])
        protocol_path.decide(seller)

        # in the predefined list, the 2nd decision is from buyer, so seller can't decide here
        self.assertRaises(ValueError, protocol_path.decide, seller)

        protocol_path.decide(buyer)

        # Now comes a new decision
        result = protocol_path.decide(seller)
        self.assertEqual([
            Decision(True, seller),
            Decision(False, buyer),
            Decision(not result, seller)
        ], protocol_path.get_alternative_decision_list())

        protocol_path.decide(buyer)
        self.assertEqual([
            Decision(True, seller),
            Decision(False, buyer),
            Decision(not result, seller)
        ], protocol_path.get_alternative_decision_list())
