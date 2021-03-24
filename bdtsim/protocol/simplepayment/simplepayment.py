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


class AbstractSimplePaymentProtocol(Protocol):
    def __init__(self, use_contract: bool):
        super(AbstractSimplePaymentProtocol, self).__init__()
        self._use_contract = use_contract
        self._contract: Optional[SolidityContract] = None

    @property
    def contract(self) -> Optional[SolidityContract]:
        return self._contract

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        if self._use_contract:
            logger.debug('deploying contract')
            self._contract = SolidityContract('SimplePayment', self.contract_path(__file__, 'SimplePayment.sol'))
            environment.deploy_contract(operator, self._contract)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        raise NotImplementedError()


class SimplePaymentPrepaidProtocol(AbstractSimplePaymentProtocol):
    def __init__(self) -> None:
        super(SimplePaymentPrepaidProtocol, self).__init__(use_contract=True)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        if self.contract is None:
            raise RuntimeError('contract not initialized')

        payment_decision = protocol_path.decide(buyer, 'pay', ('yes', 'no'))
        if payment_decision.outcome == 'yes':
            environment.send_contract_transaction(self.contract, buyer, 'pay', seller.wallet_address, value=price)

            handover_decision = protocol_path.decide(seller, 'hand over', ('yes', 'no'))
            if handover_decision.outcome == 'yes':
                environment.indicate_item_share(seller, 1, buyer)
            else:
                pass  # do not handover item
        else:
            pass  # do nothing, seller will not react


class SimplePaymentPrepaidDirectProtocol(AbstractSimplePaymentProtocol):
    def __init__(self) -> None:
        super(SimplePaymentPrepaidDirectProtocol, self).__init__(use_contract=False)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        payment_decision = protocol_path.decide(buyer, 'pay', ('yes', 'no'))
        if payment_decision.outcome == 'yes':
            environment.send_direct_transaction(buyer, seller, price)

            handover_decision = protocol_path.decide(seller, 'hand over', ('yes', 'no'))
            if handover_decision.outcome == 'yes':
                environment.indicate_item_share(seller, 1, buyer)
            else:
                pass  # do not handover item
        else:
            pass  # do nothing, seller will not react


class SimplePaymentPostpaidProtocol(AbstractSimplePaymentProtocol):
    def __init__(self) -> None:
        super(SimplePaymentPostpaidProtocol, self).__init__(use_contract=True)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        if self.contract is None:
            raise RuntimeError('contract not initialized')

        handover_decision = protocol_path.decide(seller, 'hand over', ('yes', 'no'))
        if handover_decision.outcome == 'yes':
            environment.indicate_item_share(seller, 1, buyer)

            payment_decision = protocol_path.decide(buyer, 'pay', ('yes', 'no'))
            if payment_decision.outcome == 'yes':
                environment.send_contract_transaction(self.contract, buyer, 'pay', seller.wallet_address, value=price)
            else:
                pass  # do not pay
        else:
            pass  # do not handover item, buyer will not pay


class SimplePaymentPostpaidDirectProtocol(AbstractSimplePaymentProtocol):
    def __init__(self) -> None:
        super(SimplePaymentPostpaidDirectProtocol, self).__init__(use_contract=False)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        handover_decision = protocol_path.decide(seller, 'hand over', ('yes', 'no'))
        if handover_decision.outcome == 'yes':
            environment.indicate_item_share(seller, 1, buyer)

            payment_decision = protocol_path.decide(buyer, 'pay', ('yes', 'no'))
            if payment_decision.outcome == 'yes':
                environment.send_direct_transaction(buyer, seller, price)
            else:
                pass  # do not pay
        else:
            pass  # do not handover item, buyer will not pay


ProtocolManager.register('SimplePayment-prepaid', SimplePaymentPrepaidProtocol)
ProtocolManager.register('SimplePayment-prepaid-direct', SimplePaymentPrepaidDirectProtocol)
ProtocolManager.register('SimplePayment-postpaid', SimplePaymentPostpaidProtocol)
ProtocolManager.register('SimplePayment-postpaid-direct', SimplePaymentPostpaidDirectProtocol)
