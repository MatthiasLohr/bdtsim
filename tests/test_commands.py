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

import subprocess
import unittest


class CommandTest(unittest.TestCase):
    def test_list_environments(self):
        p = subprocess.Popen(['bdtsim', 'list-environments'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join(['PyEVM', 'Web3HTTP', 'Web3Websocket', 'Web3IPC']))

    def test_list_protocols(self):
        p = subprocess.Popen(['bdtsim', 'list-protocols'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join([
            'FairSwap-FileSale',
            'SimplePayment',
            'SimplePayment-direct'
        ]))

    def test_run_simplepayment(self):
        p = subprocess.Popen(['bdtsim', 'run', 'SimplePayment', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_simplepayment_direct(self):
        p = subprocess.Popen(['bdtsim', 'run', 'SimplePayment-direct', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_fairswap_file_sale(self):
        p = subprocess.Popen(['bdtsim', 'run', 'FairSwap-FileSale', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
