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
from bdtsim.funds_diff_collection import FundsDiffCollection


seller = Account('Seller', '0x3f2c7f45cb3014e2b9d12b7fb331bdfdad6170ce5e4a0d94890aa64162569756')
buyer = Account('Buyer', '0x0633ee528dcfb901af1888d91ce451fc59a71ae7438832966811eb68ed97c173')


class FundsDiffCollectionTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(FundsDiffCollection({seller: 42}), FundsDiffCollection({seller: 42}))
        self.assertNotEqual(FundsDiffCollection({seller: 42}), FundsDiffCollection({buyer: 42}))
        self.assertNotEqual(FundsDiffCollection({seller: 42}), FundsDiffCollection({seller: 43}))

        self.assertEqual(FundsDiffCollection({seller: 42}), FundsDiffCollection({seller: 42, buyer: 0}))

    def test_iadd(self):
        fd = FundsDiffCollection({seller: 7})
        fd += FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 13}), fd)

        fd = FundsDiffCollection({seller: 7})
        fd += FundsDiffCollection({buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: 7, buyer: 6}), fd)

        fd = FundsDiffCollection({seller: 6, buyer: 7})
        fd += FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 12, buyer: 7}), fd)
        fd += FundsDiffCollection({seller: 6, buyer: 7})
        self.assertEqual(FundsDiffCollection({seller: 18, buyer: 14}), fd)

    def test_add(self):
        fd = FundsDiffCollection({seller: 7})
        fd = fd + FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 13}), fd)

        fd = FundsDiffCollection({seller: 7})
        fd = fd + FundsDiffCollection({buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: 7, buyer: 6}), fd)

        fd = FundsDiffCollection({seller: 6, buyer: 7})
        fd = fd + FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 12, buyer: 7}), fd)
        fd = fd + FundsDiffCollection({seller: 6, buyer: 7})
        self.assertEqual(FundsDiffCollection({seller: 18, buyer: 14}), fd)

    def test_isub(self):
        fd = FundsDiffCollection({seller: 7})
        fd -= FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 1}), fd)

        fd = FundsDiffCollection({seller: 7})
        fd -= FundsDiffCollection({buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: 7, buyer: -6}), fd)

        fd = FundsDiffCollection({seller: 6, buyer: 7})
        fd -= FundsDiffCollection({seller: 5})
        self.assertEqual(FundsDiffCollection({seller: 1, buyer: 7}), fd)
        fd -= FundsDiffCollection({seller: 6, buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: -5, buyer: 1}), fd)

    def test_sub(self):
        fd = FundsDiffCollection({seller: 7})
        fd = fd - FundsDiffCollection({seller: 6})
        self.assertEqual(FundsDiffCollection({seller: 1}), fd)

        fd = FundsDiffCollection({seller: 7})
        fd = fd - FundsDiffCollection({buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: 7, buyer: -6}), fd)

        fd = FundsDiffCollection({seller: 6, buyer: 7})
        fd = fd - FundsDiffCollection({seller: 5})
        self.assertEqual(FundsDiffCollection({seller: 1, buyer: 7}), fd)
        fd = fd - FundsDiffCollection({seller: 6, buyer: 6})
        self.assertEqual(FundsDiffCollection({seller: -5, buyer: 1}), fd)
