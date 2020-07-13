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
from bdtsim.account import Account
from bdtsim.protocol_path import Decision, ProtocolPath


seller = Account('Seller', '0x3f2c7f45cb3014e2b9d12b7fb331bdfdad6170ce5e4a0d94890aa64162569756')
buyer = Account('Buyer', '0x0633ee528dcfb901af1888d91ce451fc59a71ae7438832966811eb68ed97c173')


class DecisionTest(unittest.TestCase):
    def test_init(self):
        # should pass:
        Decision(seller, 'yes', ['yes', 'no'])

        self.assertRaises(ValueError, Decision, seller, 'no', ['yes'])

    def test_equals(self):
        self.assertEqual('yes', Decision(seller, 'yes', ['yes', 'no', 'maybe']))
        self.assertEqual(Decision(seller, 'yes', ['yes', 'no', 'maybe']), 'yes')
        self.assertEqual(Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                         Decision(seller, 'yes', ['yes', 'no', 'maybe']))

        self.assertNotEqual(Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                            Decision(buyer, 'yes', ['yes', 'no', 'maybe']))
        self.assertNotEqual(Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                            Decision(seller, 'no', ['yes', 'no', 'maybe']))
        self.assertNotEqual(Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                            Decision(seller, 'yes', ['yes', 'no', 'maybe', 'never']))


class ProtocolPathTest(unittest.TestCase):
    def test_get_alternatives2(self):
        path = ProtocolPath()
        path.decide(seller, '', ['yes', 'no'])
        self.assertEqual([
            ProtocolPath([Decision(seller, 'no', ['yes', 'no'])])
        ], path.get_alternatives())

        path.decide(buyer, '', ['yes', 'no'])
        self.assertEqual([
            ProtocolPath([Decision(seller, 'no', ['yes', 'no'])]),
            ProtocolPath([Decision(seller, 'yes', ['yes', 'no']), Decision(buyer, 'no', ['yes', 'no'])])
        ], path.get_alternatives())

    def test_get_alternatives3(self):
        path = ProtocolPath()
        path.decide(seller, '', ['yes', 'no', 'maybe'])
        self.assertEqual([
            ProtocolPath([Decision(seller, 'no', ['yes', 'no', 'maybe'])]),
            ProtocolPath([Decision(seller, 'maybe', ['yes', 'no', 'maybe'])])
        ], path.get_alternatives())

        path.decide(buyer, '', ['yes', 'no', 'maybe'])
        self.assertEqual([
            ProtocolPath([Decision(seller, 'no', ['yes', 'no', 'maybe'])]),
            ProtocolPath([Decision(seller, 'maybe', ['yes', 'no', 'maybe'])]),
            ProtocolPath([Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                          Decision(buyer, 'no', ['yes', 'no', 'maybe'])]),
            ProtocolPath([Decision(seller, 'yes', ['yes', 'no', 'maybe']),
                          Decision(buyer, 'maybe', ['yes', 'no', 'maybe'])])
        ], path.get_alternatives())
