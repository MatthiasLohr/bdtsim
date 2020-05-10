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

from bdtsim.account import Account, buyer, operator, seller


class AccountTest(unittest.TestCase):
    def test_instantiation(self):
        self.assertRaises(ValueError, Account, 'john')

        self.assertRaises(ValueError, Account, 'john', 'a', 'b')

        self.assertEqual(operator, Account(operator.name, wallet_private_key=operator.wallet_private_key))
        self.assertEqual(seller, Account(seller.name, wallet_private_key=seller.wallet_private_key))
        self.assertEqual(buyer, Account(buyer.name, wallet_private_key=buyer.wallet_private_key))

    def test_equals(self):
        self.assertEqual(operator, operator)
        self.assertEqual(seller, seller)
        self.assertEqual(buyer, buyer)

        self.assertEqual(operator, Account(operator.name, operator.wallet_address, operator.wallet_private_key))
        self.assertEqual(seller, Account(seller.name, seller.wallet_address, seller.wallet_private_key))
        self.assertEqual(buyer, Account(buyer.name, buyer.wallet_address, buyer.wallet_private_key))

        self.assertNotEqual(operator, seller)
        self.assertNotEqual(seller, buyer)
        self.assertNotEqual(buyer, operator)
