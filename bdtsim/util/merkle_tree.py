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

import hashlib
import math
from typing import BinaryIO, Callable, List, Union


class MerkleTreeNode(object):
    def __init__(self, *children: 'MerkleTreeNode') -> None:
        self._children = list(children)

    def digest(self, hash_alg: Union[str, Callable[[bytes], bytes]]) -> bytes:
        return get_digest(hash_alg, b''.join([c.digest(hash_alg) for c in self._children]))

    @property
    def children(self) -> List['MerkleTreeNode']:
        return self._children


class MerkleTreeLeaf(MerkleTreeNode):
    def __init__(self, data: bytes) -> None:
        super(MerkleTreeLeaf, self).__init__()
        self._data = data

    def digest(self, hash_alg: Union[str, Callable[[bytes], bytes]]) -> bytes:
        return get_digest(hash_alg, self._data)

    @property
    def data(self) -> bytes:
        return self._data


def get_digest(hash_alg: Union[str, Callable[[bytes], bytes]], data: bytes) -> bytes:
    if isinstance(hash_alg, str):
        h = hashlib.new(hash_alg)
        h.update(data)
        return h.digest()
    elif callable(hash_alg):
        return hash_alg(data)
    else:
        raise NotImplementedError('This type of hash algorithm is not supported: %s' % type(hash_alg))


def from_file(file_pointer: BinaryIO, slice_count: int) -> MerkleTreeNode:
    file_pointer.seek(0, 2)
    total_size = file_pointer.tell()
    slice_size = math.ceil(total_size / slice_count)
    file_pointer.seek(0)
    nodes: List[MerkleTreeNode] = [MerkleTreeLeaf(file_pointer.read(slice_size)) for _ in range(slice_count)]
    while len(nodes) > 1:
        nodes = [MerkleTreeNode(*nodes[i:i + 2]) for i in range(0, len(nodes), 2)]
    return nodes[0]
