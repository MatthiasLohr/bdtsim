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

from bdtsim.protocol.fairswap import FairSwap
from bdtsim.protocol.fairswap.encoding import encode, decode, B032
from bdtsim.protocol.fairswap.merkle import MerkleTreeNode, MerkleTreeLeaf, from_bytes


class FairSwapTest(unittest.TestCase):
    pass


class MerkleTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, MerkleTreeNode, MerkleTreeLeaf(B032), MerkleTreeLeaf(B032), MerkleTreeLeaf(B032))


class EncodingTest(unittest.TestCase):
    def test_encode_decode(self):
        tree = from_bytes(FairSwap.generate_bytes(128, seed=42), 4)
        tree_enc = encode(tree, B032)
        tree_dec = decode(tree_enc, B032)
        self.assertEqual(tree, tree_dec)
