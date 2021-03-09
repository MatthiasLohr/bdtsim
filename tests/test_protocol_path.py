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

from unittest import TestCase

from bdtsim.account import Account
from bdtsim.protocol_path import Choice, ProtocolPath


seller = Account('Seller', '0x3f2c7f45cb3014e2b9d12b7fb331bdfdad6170ce5e4a0d94890aa64162569756')
buyer = Account('Buyer', '0x0633ee528dcfb901af1888d91ce451fc59a71ae7438832966811eb68ed97c173')


class ChoiceTest(TestCase):
    def test_init(self) -> None:
        # should pass
        Choice(seller, ('yes', 'no'))

        # should not pass
        self.assertRaises(ValueError, Choice, seller, ('yes', ))  # complain about single choice
        self.assertRaises(ValueError, Choice, seller, ('yes', 'no'), ('maybe', ))  # honest choice(s) not in choices

    def test_eq(self) -> None:
        choice1 = Choice(seller, ('yes', 'no'))
        choice2 = Choice(seller, ('yes', 'no'))

        self.assertEqual(choice1, choice1)  # a choice should be equal to itself
        self.assertNotEqual(choice1, choice2)  # a choice should not be equal to a copy of the choice

    def test_choose(self) -> None:
        choice = Choice(seller, ('yes', 'no'))

        self.assertRaises(ValueError, choice.choose, 'maybe')  # not an allowed choice

        decision_yes = choice.choose('yes')
        decision_no = choice.choose('no')

        self.assertNotEqual(decision_yes, decision_no)  # different outcomes from same choice should be unequal
        self.assertEqual(decision_yes, choice.choose('yes'))  # same outcomes from same choice should be equal


class DecisionTest(TestCase):
    def test_eq(self) -> None:
        choice1 = Choice(seller, ('yes', 'no'))
        choice2 = Choice(seller, ('yes', 'no'))

        # same outcomes from same choice should be equal
        self.assertEqual(choice1.choose('yes'), choice1.choose('yes'))
        # same outcomes frmo different choices should not be equal (since different choice)
        self.assertNotEqual(choice1.choose('yes'), choice2.choose('yes'))
        # different outcomes from same choice should be unequal
        self.assertNotEqual(choice1.choose('yes'), choice1.choose('no'))


class ProtocolPathTest(TestCase):
    def test_decide(self) -> None:
        protocol_path = ProtocolPath()
        decision = protocol_path.decide(seller, 'should I sell or should I buy', ('sell', 'buy'))

        self.assertEqual('sell', decision.outcome)  # first outcome of protocol path decide should be first option

    def test_get_alternatives(self) -> None:
        pp_initial = ProtocolPath()
        decision1 = pp_initial.decide(seller, 'should I sell or should I buy', ('sell', 'buy'))
        pp_alternatives = pp_initial.get_alternatives()
        # with a two-option choice and a done decision, there should be 1 alternative
        self.assertEqual(1, len(pp_alternatives))

        decision2 = pp_alternatives[0].decide(seller, 'should I sell or should I buy', ('sell', 'buy'))
        # both decisions from same protocol path and protocol path position should be based on same choice:
        self.assertEqual(decision1.choice, decision2.choice)
        # alternative path decision should have different outcome:
        self.assertNotEqual(decision1.outcome, decision2.outcome)
        # alternative path decisions should be different (since outcome is different):
        self.assertNotEqual(decision1, decision2)

    def test_get_alternatives2(self) -> None:
        pp_initial = ProtocolPath()
        pp_initial.decide(seller, 'should I sell or should I buy', ('sell', 'buy'))
        pp_alternatives = pp_initial.get_alternatives()
        # alternative path decision with different decision description should not be allowed:
        self.assertRaises(
            ValueError,
            pp_alternatives[0].decide, seller, 'should I STAY or should I GO', ('sell', 'buy')
        )

    def test_get_alternatives3(self) -> None:
        pp_initial = ProtocolPath()
        pp_initial.decide(seller, 'should I sell or should I buy', ('sell', 'buy'))
        pp_alternatives = pp_initial.get_alternatives()
        # alternative path decision with different options should not be allowed:
        self.assertRaises(
            ValueError,
            pp_alternatives[0].decide, seller, 'should I sell or should I buy', ('yes', 'no')
        )

    def test_get_alternatives4(self) -> None:
        pp_initial = ProtocolPath()
        pp_initial.decide(seller, 'should I sell or should I buy', ('sell', 'buy'))
        pp_alternatives = pp_initial.get_alternatives()
        # alternative path decision with different honest options should not be allowed:
        self.assertRaises(
            ValueError,
            pp_alternatives[0].decide, seller, 'should I sell or should I buy', ('sell', 'buy'), ('sell', 'buy')
        )
