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
import unittest
from bdtsim.protocol_path import ProtocolPath


class ProtocolPathTest(unittest.TestCase):
    def test_get_alternatives(self):
        self.assertEqual([], ProtocolPath.get_alternative_paths([]))

        self.assertEqual([[False]], ProtocolPath.get_alternative_paths([True]))
        self.assertEqual([[True]], ProtocolPath.get_alternative_paths([False]))

        all_paths = [list(p) for p in itertools.product((True, False), repeat=3)]
        for i in range(len(all_paths)):
            path = all_paths[i]
            alternative_paths = all_paths[0:i] + all_paths[i+1:]
            self.assertEqual(alternative_paths, ProtocolPath.get_alternative_paths(path))
