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

from web3 import Web3

from bdtsim.util.xor import xor_crypt
from .merkle import MerkleTreeNode, MerkleTreeLeaf, from_list


B032 = b'\x00' * 32


class DecodingError(Exception):
    pass


class DigestMismatchError(DecodingError):
    def __init__(self) -> None:
        pass


def crypt(value: bytes, index: int, key: bytes) -> bytes:
    return xor_crypt(value, Web3.solidityKeccak(['uint256', 'bytes32'], [index, key]))


def encode(root: MerkleTreeNode, key: bytes) -> MerkleTreeNode:
    leaves_enc = [crypt(bytes(leaf), index, key) for index, leaf in enumerate(root.leaves)]
    digests_enc = [crypt(digest, index + len(leaves_enc), key) for index, digest in enumerate(root.digests_pack)]
    return from_list(leaves_enc + digests_enc + [B032])


def decode(root: MerkleTreeNode, key: bytes) -> MerkleTreeNode:
    leaf_bytes_enc = root.leaves
    if not math.log2(len(leaf_bytes_enc)).is_integer():
        raise ValueError('Merkle Tree must have 2^x leaves')
    if leaf_bytes_enc[-1] != B032:
        raise ValueError('The provided Merkle Tree does not appear to be encoded')

    digest_start_index = int(len(leaf_bytes_enc) / 2)
    digest_index = digest_start_index
    nodes: List[MerkleTreeNode] = [MerkleTreeLeaf(crypt(bytes(leaf_bytes_enc[i]), i, key))
                                   for i in range(0, digest_start_index)]
    while len(nodes) > 1:
        nodes_new = []
        for i in range(0, len(nodes), 2):
            node = MerkleTreeNode(nodes[i], nodes[i + 1])
            if node.digest == crypt(bytes(leaf_bytes_enc[digest_index]), digest_index, key):
                digest_index += 1
                nodes_new.append(node)
            else:
                raise DigestMismatchError()
        nodes = nodes_new

    return nodes[0]
