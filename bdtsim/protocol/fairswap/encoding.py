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
from typing import List, Tuple, Type

from web3 import Web3

from bdtsim.util.xor import xor_crypt
from .merkle import MerkleTreeNode, MerkleTreeLeaf, MerkleTreeHashLeaf, from_leaves


B032 = b'\x00' * 32


class DecodingError(Exception):
    pass


class NodeDigestMismatchError(DecodingError):
    def __init__(self, in1: MerkleTreeLeaf, in2: MerkleTreeLeaf, out: MerkleTreeLeaf, index_in: int,
                 index_out: int, expected_digest: bytes, actual_digest: bytes) -> None:
        self.in1 = in1
        self.in2 = in2
        self.out = out
        self.index_in = index_in
        self.index_out = index_out
        self.expected_digest = expected_digest
        self.actual_digest = actual_digest


class LeafDigestMismatchError(NodeDigestMismatchError):
    pass


def crypt(value: bytes, index: int, key: bytes) -> bytes:
    return xor_crypt(value, Web3.solidityKeccak(['uint256', 'bytes32'], [index, key]))


def encode(root: MerkleTreeNode, key: bytes) -> MerkleTreeNode:
    leaves_enc = [crypt(leaf.data, index, key) for index, leaf in enumerate(root.leaves)]
    digests_enc = [crypt(digest, 2 * len(leaves_enc) + index, key) for index, digest in enumerate(root.digests_pack)]
    return from_leaves([MerkleTreeLeaf(x) for x in leaves_enc]
                       + [MerkleTreeHashLeaf(x) for x in digests_enc]
                       + [MerkleTreeHashLeaf(B032)])


def decode(root: MerkleTreeNode, key: bytes) -> Tuple[MerkleTreeNode, List[NodeDigestMismatchError]]:
    leaf_bytes_enc = root.leaves
    if not math.log2(len(leaf_bytes_enc)).is_integer():
        raise ValueError('Merkle Tree must have 2^x leaves')
    if leaf_bytes_enc[-1] != B032:
        raise ValueError('The provided Merkle Tree does not appear to be encoded')

    errors: List[NodeDigestMismatchError] = []
    digest_start_index = int(len(leaf_bytes_enc) / 2)
    node_index = 0
    digest_index = digest_start_index
    nodes: List[MerkleTreeNode] = [MerkleTreeLeaf(crypt(leaf_bytes_enc[i].data, i, key))
                                   for i in range(0, digest_start_index)]
    while len(nodes) > 1:
        nodes_new = []
        for i in range(0, len(nodes), 2):
            node = MerkleTreeNode(nodes[i], nodes[i + 1])
            expected_digest = crypt(leaf_bytes_enc[digest_index].data, digest_start_index + digest_index, key)

            if node_index < digest_start_index:
                error_type: Type[NodeDigestMismatchError] = LeafDigestMismatchError
                actual_digest = node.digest
            else:
                error_type = NodeDigestMismatchError
                actual_digest = Web3.solidityKeccak(['bytes32', 'bytes32'], [
                    crypt(leaf_bytes_enc[node_index].data, digest_start_index + node_index, key),
                    crypt(leaf_bytes_enc[node_index + 1].data, digest_start_index + node_index + 1, key)
                ])

            if expected_digest != actual_digest:
                errors.append(error_type(
                    in1=leaf_bytes_enc[node_index],
                    in2=leaf_bytes_enc[node_index + 1],
                    out=leaf_bytes_enc[digest_index],
                    index_in=node_index,
                    index_out=digest_index,
                    expected_digest=expected_digest,
                    actual_digest=actual_digest
                ))

            node_index += 2
            digest_index += 1
            nodes_new.append(node)

        nodes = nodes_new

    return nodes[0], errors
