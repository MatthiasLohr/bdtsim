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

from bdtsim.util.filesize import FileSize


class UtilFileSizeTest(unittest.TestCase):
    def test_init_eq(self):
        self.assertRaises(ValueError, FileSize, 1.3)

        self.assertEqual(FileSize(123), FileSize(123))
        self.assertEqual(123, FileSize(123))
        self.assertEqual(1000000, FileSize('1M'))
        self.assertEqual(FileSize('1000k'), FileSize('1M'))
        self.assertEqual(1300, FileSize('1.3k'))

    def test_format_bytes(self):
        self.assertEqual('1k', FileSize(1000).human_readable())
        self.assertEqual('1M', FileSize(1000000).human_readable())
        self.assertEqual('1G', FileSize(1000000000).human_readable())
        self.assertEqual('150k', FileSize(150000).human_readable())
