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

from .. import Protocol, ProtocolRegistration, SolidityContract


class SimplePayment(Protocol):

    @property
    def contract_reusable(self):
        return True

    @property
    def contract(self):
        return SolidityContract(self.contract_path(__file__, 'SimplePayment.sol'), 'SimplePayment')

    def run(self):
        pass


ProtocolRegistration.register('SimplePayment', SimplePayment)
