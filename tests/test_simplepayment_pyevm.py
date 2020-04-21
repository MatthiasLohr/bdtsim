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
from bdtsim.data_provider import GenericDataProvider
from bdtsim.environment import EnvironmentManager
from bdtsim.protocol import ProtocolManager
from bdtsim.simulation import Simulation


class SimplePaymentPyEVMTests(unittest.TestCase):
    def test_simple_payment_pyevm_direct(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment-direct'),
            environment=EnvironmentManager.instantiate('PyEVM', chain_id=61),
            data_provider=GenericDataProvider()
        )
        result = simulation.run()
        self.assertIsNotNone(result)

    def test_simple_payment_pyevm_indirect(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment'),
            environment=EnvironmentManager.instantiate('PyEVM', chain_id=61),
            data_provider=GenericDataProvider()
        )
        result = simulation.run()
        self.assertIsNotNone(result)
