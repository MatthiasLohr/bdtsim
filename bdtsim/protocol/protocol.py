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

import os


class Protocol(object):
    def __init__(self, seller=None, buyer=None, operator=None, contract_address=None):
        self._seller = seller
        self._buyer = buyer
        self._operator = operator
        self._contract_address = contract_address

    def monitor(self, role):
        return Monitor(role)

    def run(self):
        raise NotImplementedError()

    def deploy_contract(self):
        with self.monitor(self._operator):
            return self._operator.deploy_contract(self.contract)

    @property
    def seller(self):
        return self._seller

    @property
    def buyer(self):
        return self._buyer

    @property
    def contract_reusable(self):
        raise NotImplementedError()

    @property
    def contract(self):
        raise NotImplementedError()

    @staticmethod
    def contract_path(file_var, filename):
        return os.path.join(os.path.dirname(file_var), filename)


class Monitor(object):
    def __init__(self, role):
        self._role = role

    def __enter__(self):
        return self._role

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
