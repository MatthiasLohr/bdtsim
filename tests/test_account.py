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

from bdtsim.account import Account, AccountFile


class AccountTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AccountTest, self).__init__(*args, **kwargs)
        account_file = AccountFile()
        self.operator = account_file.operator
        self.seller = account_file.seller
        self.buyer = account_file.buyer

    def test_instantiation(self):
        self.assertRaises(ValueError, Account, 'john', 'a')

        self.assertEqual(self.operator, Account(self.operator.name, self.operator.wallet_private_key))
        self.assertEqual(self.seller, Account(self.seller.name, self.seller.wallet_private_key))
        self.assertEqual(self.buyer, Account(self.buyer.name, self.buyer.wallet_private_key))

    def test_equals(self):
        self.assertEqual(self.operator, self.operator)
        self.assertEqual(self.seller, self.seller)
        self.assertEqual(self.buyer, self.buyer)

        self.assertNotEqual(self.operator, self.seller)
        self.assertNotEqual(self.seller, self.buyer)
        self.assertNotEqual(self.buyer, self.operator)
