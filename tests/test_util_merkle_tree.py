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

from bdtsim.data_provider import RandomDataProvider
from bdtsim.util import merkle_tree


class UtilMerkleTreeTest(unittest.TestCase):
    def test_from_file(self):
        data_provider = RandomDataProvider(size=15, seed=42)
        merkle_tree_root = merkle_tree.from_file(data_provider.file_pointer, 4)
        last_leaf = merkle_tree_root.children[1].children[1]
        self.assertIsInstance(last_leaf, merkle_tree.MerkleTreeLeaf)
        self.assertEqual(3, len(last_leaf.data))
        self.assertEqual('67b7786d13996b4e46375ceb603ef57707487107', merkle_tree_root.digest('sha1').hex())
