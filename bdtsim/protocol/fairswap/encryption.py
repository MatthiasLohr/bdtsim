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

import math
from typing import List

from bdtsim.util.xor import xor_crypt
from . import merkle


class DecryptionError(Exception):
    pass


def encrypt_merkle_tree(root: merkle.MerkleTreeNode, key: bytes) -> merkle.MerkleTreeNode:
    leaves_encrypted = [xor_crypt(bytes(leaf), key) for leaf in root.leaves]
    digests_encrypted = [xor_crypt(digest, key) for digest in root.digests_pack]
    return merkle.from_list(leaves_encrypted + digests_encrypted)


def decrypt_merkle_tree(root: merkle.MerkleTreeNode, key: bytes) -> merkle.MerkleTreeNode:
    data_decrypted = [xor_crypt(bytes(leaf_enc), key) for leaf_enc in root.leaves]
    if not math.log2(len(data_decrypted) + 1).is_integer():
        raise ValueError('Number of leaves + 1 must be power of 2')
    leaf_data = data_decrypted[:int((len(data_decrypted) + 1) / 2)]
    digests = data_decrypted[int((len(data_decrypted) + 1) / 2):]

    nodes: List[merkle.MerkleTreeNode] = [merkle.MerkleTreeLeaf(d) for d in leaf_data]
    while len(nodes) > 1:
        nodes = [merkle.MerkleTreeNode(*nodes[i:i + 2]) for i in range(0, len(nodes), 2)]
        for node in nodes:
            node_digest = digests.pop(0)
            if node.digest != node_digest:
                raise DecryptionError('Digest mismatch')
    return nodes[0]
