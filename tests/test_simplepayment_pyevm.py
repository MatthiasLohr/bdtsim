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

from bdtsim.account import AccountFile
from bdtsim.data_provider import RandomDataProvider
from bdtsim.environment import EnvironmentManager
from bdtsim.protocol import ProtocolManager
from bdtsim.simulation import Simulation


class SimplePaymentPyEVMTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SimplePaymentPyEVMTests, self).__init__(*args, **kwargs)
        account_file = AccountFile()
        self.operator = account_file.operator
        self.seller = account_file.seller
        self.buyer = account_file.buyer

    def test_simple_payment_pyevm_prepaid(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment-prepaid'),
            environment=EnvironmentManager.instantiate('PyEVM', operator=self.operator, seller=self.seller,
                                                       buyer=self.buyer, chain_id=61),
            data_provider=RandomDataProvider(),
            operator=self.operator,
            seller=self.seller,
            buyer=self.buyer
        )
        result = simulation.run()
        self.assertIsNotNone(result)

    def test_simple_payment_pyevm_prepaid_direct(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment-prepaid-direct'),
            environment=EnvironmentManager.instantiate('PyEVM', operator=self.operator, seller=self.seller,
                                                       buyer=self.buyer, chain_id=61),
            data_provider=RandomDataProvider(),
            operator=self.operator,
            seller=self.seller,
            buyer=self.buyer
        )
        result = simulation.run()
        self.assertIsNotNone(result)

    def test_simple_payment_pyevm_postpaid(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment-postpaid'),
            environment=EnvironmentManager.instantiate('PyEVM', operator=self.operator, seller=self.seller,
                                                       buyer=self.buyer, chain_id=61),
            data_provider=RandomDataProvider(),
            operator=self.operator,
            seller=self.seller,
            buyer=self.buyer
        )
        result = simulation.run()
        self.assertIsNotNone(result)

    def test_simple_payment_pyevm_postpaid_direct(self):
        simulation = Simulation(
            protocol=ProtocolManager.instantiate('SimplePayment-postpaid-direct'),
            environment=EnvironmentManager.instantiate('PyEVM', operator=self.operator, seller=self.seller,
                                                       buyer=self.buyer, chain_id=61),
            data_provider=RandomDataProvider(),
            operator=self.operator,
            seller=self.seller,
            buyer=self.buyer
        )
        result = simulation.run()
        self.assertIsNotNone(result)
