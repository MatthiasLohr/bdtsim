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


class BlockchainEnvironment(object):
    def __init__(self, web3_provider, chain_id, gas_price=None, gas_price_factor=1, tx_wait_timeout=120):
        self._web3_provider = web3_provider
        self._chain_id = chain_id
        self._gas_price = gas_price
        self._gas_price_factor = gas_price_factor
        self._tx_wait_timeout = tx_wait_timeout

    def set_up(self):
        raise NotImplementedError()

    def strip_down(self):
        raise NotImplementedError()

    @property
    def web3_provider(self):
        return self._web3_provider

    @property
    def chain_id(self):
        return self._chain_id

    @property
    def gas_price(self):
        return self._gas_price

    @property
    def gas_price_factor(self):
        return self._gas_price_factor

    @property
    def tx_wait_timeout(self):
        return self._tx_wait_timeout
