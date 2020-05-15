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

from eth_utils.crypto import keccak


class MerkleTreeNode(object):
    def __init__(self, *children: 'MerkleTreeNode') -> None:
        self._children = list(children)

    @property
    def children(self) -> List['MerkleTreeNode']:
        return self._children

    @property
    def digest(self) -> bytes:
        return keccak(b''.join([bytes(child) for child in self.children]))

    def __bytes__(self) -> bytes:
        return self.digest


class MerkleTreeLeaf(MerkleTreeNode):
    def __init__(self, data: bytes) -> None:
        super(MerkleTreeLeaf, self).__init__()
        self._data = data

    @property
    def data(self) -> bytes:
        return self._data

    def __bytes__(self) -> bytes:
        return self.data


def from_leaves(leaves: List[MerkleTreeLeaf]) -> MerkleTreeNode:
    nodes = leaves
    while len(nodes) > 1:
        nodes = [MerkleTreeNode(*nodes[i:i + 2]) for i in range(0, len(nodes), 2)]
    return nodes[0]


def from_bytes(data: bytes, slices_count: int = 8) -> MerkleTreeNode:
    if slices_count < 2 or not math.log2(slices_count).is_integer():
        raise ValueError('slices_count must be >= 2 integer and power of 2')
    slice_len = math.ceil(len(data) / slices_count)
    return from_leaves([MerkleTreeLeaf(data[slice_len * s:slice_len * (s + 1)]) for s in range(slices_count)])
