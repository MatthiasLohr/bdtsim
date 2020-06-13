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

import logging

from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.account import Account
from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class SimplePayment(Protocol):
    """Example implementation of SimplePayment (paying after exchange, direct payments)"""
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        release_goods = protocol_path.decide(seller, 'release goods?', ['yes', 'no'])
        # [...] seller releases goods to buyer, not monitored by BDTsim
        if release_goods == 'yes':
            pay = protocol_path.decide(buyer, 'pay?', ['yes', 'no'])
            if pay == 'yes':
                environment.send_direct_transaction(buyer, seller, price)
            else:
                pass  # buyer left protocol, having goods, without payment
        else:
            pass  # seller left protocol, no reaction from buyer


class AbstractParameterizedSimplePayment(Protocol):
    def __init__(self, use_contract: bool):
        super(AbstractParameterizedSimplePayment, self).__init__()
        self._use_contract = use_contract

    def get_contract(self) -> SolidityContract:
        return SolidityContract('SimplePayment', self.contract_path(__file__, 'SimplePayment.sol'))

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        if self._use_contract:
            logger.debug('Deploying contract...')
            environment.deploy_contract(operator, self.get_contract())

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        raise NotImplementedError()


class SimplePaymentPrepaid(AbstractParameterizedSimplePayment):
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        if protocol_path.decide(buyer, description='Payment', variants=['paying', 'not paying']).is_honest():
            logger.debug('Decided to be honest')
            if self._use_contract:
                environment.send_contract_transaction(buyer, 'pay', seller.wallet_address, value=price)
            else:
                environment.send_direct_transaction(buyer, seller, price)

            protocol_path.decide(seller, description='Give goods', variants=['yes', 'no'])
        else:
            logger.debug('Decided to cheat')  # do nothing


class SimplePaymentPostpaid(AbstractParameterizedSimplePayment):
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        if protocol_path.decide(seller, 'Give goods', ['yes', 'no']).is_honest():
            if protocol_path.decide(buyer, description='Payment', variants=['paying', 'not paying']).is_honest():
                logger.debug('Decided to be honest')
                if self._use_contract:
                    environment.send_contract_transaction(buyer, 'pay', seller.wallet_address, value=price)
                else:
                    environment.send_direct_transaction(buyer, seller, price)


ProtocolManager.register('SimplePayment', SimplePayment)
ProtocolManager.register('SimplePayment-prepaid', SimplePaymentPrepaid, use_contract=True)
ProtocolManager.register('SimplePayment-prepaid-direct', SimplePaymentPrepaid, use_contract=False)
ProtocolManager.register('SimplePayment-postpaid', SimplePaymentPostpaid, use_contract=True)
ProtocolManager.register('SimplePayment-postpaid-direct', SimplePaymentPostpaid, use_contract=False)
