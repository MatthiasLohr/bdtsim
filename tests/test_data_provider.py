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


class RandomDataProviderTest(unittest.TestCase):
    def test_random_data_provider_size(self):
        for size in 0, 1, 13, 42, 1337, 1000000:
            data_provider = RandomDataProvider(size)
            fp = data_provider.file_pointer
            fp.seek(0, 2)
            self.assertEqual(size, fp.tell())

    def test_random_data_provider_seed(self):
        data = RandomDataProvider(size=4, seed=42).file_pointer.read()
        self.assertEqual(b'\xa3\x1c\x06\xbd', data)
        data = RandomDataProvider(size=4, seed=42).file_pointer.read()
        self.assertEqual(b'\xa3\x1c\x06\xbd', data)
        data = RandomDataProvider(size=4, seed=43).file_pointer.read()
        self.assertEqual(b'\tI\xb2\xc3', data)
        data = RandomDataProvider(size=4, seed=42).file_pointer.read()
        self.assertEqual(b'\xa3\x1c\x06\xbd', data)
