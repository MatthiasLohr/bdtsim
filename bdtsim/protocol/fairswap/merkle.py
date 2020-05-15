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

import itertools
import math
from typing import List, Tuple

from eth_utils.crypto import keccak


class MerkleTreeNode(object):
    def __init__(self, *children: 'MerkleTreeNode') -> None:
        if len(children) > 2:
            raise ValueError('A node can have at max 2 children')
        self._children = list(children)

    @property
    def children(self) -> List['MerkleTreeNode']:
        return self._children

    @property
    def leaves(self) -> List['MerkleTreeLeaf']:
        return list(itertools.chain.from_iterable([c.leaves for c in self.children]))

    @property
    def digest(self) -> bytes:
        return keccak(b''.join([bytes(child) for child in self.children]))

    @property
    def digests_dfs(self) -> List[bytes]:
        return list(itertools.chain.from_iterable([c.digests_dfs for c in self.children])) + [self.digest]

    @property
    def digests_pack(self) -> List[bytes]:
        return [digest for digest, level in sorted(self._digests_pack(0), key=lambda d: d[1], reverse=True)]

    def _digests_pack(self, level) -> List[Tuple[bytes, int]]:
        return list(itertools.chain.from_iterable([
            c._digests_pack(level + 1) for c in self.children
        ])) + [(self.digest, level)]

    def __bytes__(self) -> bytes:
        return self.digest

    def __repr__(self) -> str:
        return '<%s.%s %s>' % (
            __name__,
            MerkleTreeNode.__name__,
            self.digest.hex()
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, MerkleTreeNode):
            return self.digest == other.digest
        else:
            return NotImplemented

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class MerkleTreeLeaf(MerkleTreeNode):
    def __init__(self, data: bytes) -> None:
        super(MerkleTreeLeaf, self).__init__()
        self._data = data

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def leaves(self) -> List['MerkleTreeLeaf']:
        return [self]

    @property
    def digests_dfs(self) -> List[bytes]:
        return []

    @property
    def digests_pack(self) -> List[bytes]:
        return []

    def _digests_pack(self, level) -> List[Tuple[bytes, int]]:
        return []

    def __bytes__(self) -> bytes:
        return self.data

    def __repr__(self) -> str:
        return '<%s.%s %s>' % (
            __name__,
            MerkleTreeLeaf.__name__,
            str(self.data)
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, MerkleTreeLeaf):
            return self.data == other.data
        else:
            return NotImplemented

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


def from_leaves(leaves: List[MerkleTreeLeaf]) -> MerkleTreeNode:
    if len(leaves) == 0:
        raise ValueError('Cannot create tree from empty list')
    nodes = leaves
    while len(nodes) > 1:
        nodes = [MerkleTreeNode(*nodes[i:i + 2]) for i in range(0, len(nodes), 2)]
    return nodes[0]


def from_bytes(data: bytes, slices_count: int = 8) -> MerkleTreeNode:
    if slices_count < 2 or not math.log2(slices_count).is_integer():
        raise ValueError('slices_count must be >= 2 integer and power of 2')
    slice_len = math.ceil(len(data) / slices_count)
    return from_leaves([MerkleTreeLeaf(data[slice_len * s:slice_len * (s + 1)]) for s in range(slices_count)])


def from_list(items: List[bytes]) -> MerkleTreeNode:
    return from_leaves([MerkleTreeLeaf(item) for item in items])
