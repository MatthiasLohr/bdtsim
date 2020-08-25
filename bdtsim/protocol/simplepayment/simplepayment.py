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
from typing import Optional

from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.account import Account
from bdtsim.protocol import Protocol, ProtocolManager, DEFAULT_ASSET_PRICE
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class SimplePayment(Protocol):
    """Example implementation of SimplePayment (paying after exchange, direct payments)"""
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        """

        Args:
            protocol_path (ProtocolPath): Protocol path this simulation for a data exchange will take
            environment (Environment): The environment (blockchain) in which the protocol interactions will take place
            data_provider (DataProvider): The data to be traded
            seller (Account): The selling party
            buyer (Account): The buying party
            price (int): Price for the data/asset to be traded (in Wei)

        Returns:
            None
        """
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
        self._contract: Optional[SolidityContract] = None

    @property
    def contract(self) -> SolidityContract:
        if self._contract is not None:
            return self._contract
        else:
            raise RuntimeError('Contract not initialized')

    def get_contract(self) -> SolidityContract:
        return SolidityContract('SimplePayment', self.contract_path(__file__, 'SimplePayment.sol'))

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        if self._use_contract:
            logger.debug('Deploying contract...')
            self._contract = self.get_contract()
            environment.deploy_contract(operator, self.contract)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        """

        Args:
            protocol_path (ProtocolPath): Protocol path this simulation for a data exchange will take
            environment (Environment): The environment (blockchain) in which the protocol interactions will take place
            data_provider (DataProvider): The data to be traded
            seller (Account): The selling party
            buyer (Account): The buying party
            price (int): Price for the data/asset to be traded (in Wei)

        Returns:
            None
        """
        raise NotImplementedError()


class SimplePaymentPrepaid(AbstractParameterizedSimplePayment):
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        """

        Args:
            protocol_path (ProtocolPath): Protocol path this simulation for a data exchange will take
            environment (Environment): The environment (blockchain) in which the protocol interactions will take place
            data_provider (DataProvider): The data to be traded
            seller (Account): The selling party
            buyer (Account): The buying party
            price (int): Price for the data/asset to be traded (in Wei)

        Returns:
            None
        """
        if protocol_path.decide(buyer, description='Payment', variants=['paying', 'not paying']).is_honest():
            logger.debug('Decided to be honest')
            if self._use_contract:
                environment.send_contract_transaction(self.contract, buyer, 'pay', seller.wallet_address, value=price)
            else:
                environment.send_direct_transaction(buyer, seller, price)

            protocol_path.decide(seller, description='Give goods', variants=['yes', 'no'])
        else:
            logger.debug('Decided to cheat')  # do nothing


class SimplePaymentPostpaid(AbstractParameterizedSimplePayment):
    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        """

        Args:
            protocol_path (ProtocolPath): Protocol path this simulation for a data exchange will take
            environment (Environment): The environment (blockchain) in which the protocol interactions will take place
            data_provider (DataProvider): The data to be traded
            seller (Account): The selling party
            buyer (Account): The buying party
            price (int): Price for the data/asset to be traded (in Wei)

        Returns:
            None
        """
        if protocol_path.decide(seller, 'Give goods', ['yes', 'no']).is_honest():
            if protocol_path.decide(buyer, description='Payment', variants=['paying', 'not paying']).is_honest():
                logger.debug('Decided to be honest')
                if self._use_contract:
                    environment.send_contract_transaction(self.contract, buyer, 'pay', seller.wallet_address,
                                                          value=price)
                else:
                    environment.send_direct_transaction(buyer, seller, price)


ProtocolManager.register('SimplePayment', SimplePayment)
ProtocolManager.register('SimplePayment-prepaid', SimplePaymentPrepaid, use_contract=True)
ProtocolManager.register('SimplePayment-prepaid-direct', SimplePaymentPrepaid, use_contract=False)
ProtocolManager.register('SimplePayment-postpaid', SimplePaymentPostpaid, use_contract=True)
ProtocolManager.register('SimplePayment-postpaid-direct', SimplePaymentPostpaid, use_contract=False)
