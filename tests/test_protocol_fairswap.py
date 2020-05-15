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

from bdtsim.protocol.fairswap import encryption, merkle


class FairSwapProtocolMerkleTest(unittest.TestCase):
    def test_from_bytes(self):
        self.assertRaises(ValueError, merkle.from_bytes, b'1234', -1)
        self.assertRaises(ValueError, merkle.from_bytes, b'1234', 1)
        self.assertRaises(ValueError, merkle.from_bytes, b'1234', 3)

        tree = merkle.from_bytes(b'aabbccddeeffgghh', 8)
        ff_child = tree.children[1].children[0].children[1]
        self.assertIsInstance(ff_child, merkle.MerkleTreeNode)
        self.assertEqual(b'ff', bytes(ff_child))

    def test_digests_pack(self):
        tree = merkle.from_bytes(b'ab', 2)
        self.assertEqual(1, len(tree.digests_pack))


class FairSwapProtocolEncryptionTest(unittest.TestCase):
    def test_encrypt_decrypt(self):
        tree = merkle.from_bytes(b'aabbccddeeffgghh', 8)
        key = b'13374242'
        tree_enc = encryption.encrypt_merkle_tree(tree, key)
        tree_dec = encryption.decrypt_merkle_tree(tree_enc, key)
        self.assertEqual(tree, tree_dec)
