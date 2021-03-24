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
from unittest import TestCase


class CommandTest(TestCase):
    def test_list_environments(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'list-environments'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join(['PyEVM', 'Web3HTTP', 'Web3Websocket', 'Web3IPC']))

    def test_list_protocols(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'list-protocols'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join([
            'Delgado',
            'Delgado-ReusableLibrary',
            'Delgado-ReusableContract',
            'FairSwap',
            'FairSwap-Reusable',
            'SimplePayment-prepaid',
            'SimplePayment-prepaid-direct',
            'SimplePayment-postpaid',
            'SimplePayment-postpaid-direct',
            'SmartJudge-FairSwap'
        ]))

    def test_list_data_providers(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'list-data-providers'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join([
            'RandomDataProvider',
            'FileDataProvider'
        ]))

    def test_list_renderers(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'list-renderers'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out.decode('utf-8').strip(), '\n'.join([
            'game-matrix',
            'game-tree',
            'dot'
        ]))

    def test_run_simplepayment_prepaid(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'SimplePayment-prepaid', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_simplepayment_prepaid_direct(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'SimplePayment-prepaid-direct', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_simplepayment_postpaid(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'SimplePayment-postpaid', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_simplepayment_postpaid_direct(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'SimplePayment-postpaid-direct', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_fairswap(self) -> None:
        p = subprocess.Popen(
            ['env', 'bdtsim', 'run', 'FairSwap', 'PyEVM', '-d', 'size', '256', '-p', 'slices-count', '8'],
            stdout=subprocess.PIPE
        )
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_fairswap_reusable(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'FairSwap-Reusable', 'PyEVM', '-d', 'size', '256',
                              '-p', 'slices-count', '8'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_delgado(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'Delgado', 'PyEVM'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_delgado_reusable_library(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'Delgado-ReusableLibrary', 'PyEVM'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_delgado_reusable_contract(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'Delgado-ReusableContract', 'PyEVM'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_run_smartjudge_fairswap(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'run', 'SmartJudge-FairSwap', 'PyEVM', '-d', 'size', '128',
                              '-p', 'slices-count', '4', '-p', 'slice_length', '32'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)

    def test_environment_info_pyevm(self) -> None:
        p = subprocess.Popen(['env', 'bdtsim', 'environment-info', 'PyEVM'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0)
