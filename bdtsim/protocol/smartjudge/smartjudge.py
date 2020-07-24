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
from typing import Any

from web3 import Web3

from bdtsim.account import Account
from bdtsim.contract import SolidityContractCollection
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, ProtocolExecutionError
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class SmartJudge(Protocol):
    def __init__(self, worst_cast_cost: int = 1000000, security_deposit: int = 4000000, timeout: int = 86400,
                 *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._worst_case_cost = worst_cast_cost
        self._security_deposit = security_deposit
        self._timeout = timeout

        contract_collection = SolidityContractCollection(solc_version='0.4.26')
        contract_collection.add_contract_template_file('Mediator', self.contract_path(__file__, 'mediator.tpl.sol'), {
            'security_deposit': security_deposit,
            'timeout': timeout
        }, 'mediator.sol')
        contract_collection.add_contract_file('fileSale', self.contract_path(__file__, 'verifier-fairswap.sol'))

        self._mediator_contract = contract_collection.get('Mediator')
        self._verifier_contract = contract_collection.get('fileSale')

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        environment.deploy_contract(operator, self._mediator_contract, False)
        environment.deploy_contract(operator, self._verifier_contract, False, self._mediator_contract.address)
        environment.send_contract_transaction(
            self._mediator_contract,
            operator,
            'register_verifier',
            self._verifier_contract.address,
            self._worst_case_cost
        )

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:

        # === buyer prepares new trade
        logger.debug('Buyer prepares new trade')
        agreement_hash = Web3.soliditySha3(['bytes'], [b'abc'])
        environment.send_contract_transaction(self._mediator_contract, buyer, 'create', agreement_hash,
                                              value=self._security_deposit * environment.gas_price)
        trade_id = None
        for event in environment.event_filter(self._mediator_contract, 'TradeID', from_block=-1):
            trade_id = event['args']['_id']
            logger.debug('This trade has id %i' % trade_id)
            break

        acceptance_decision = protocol_path.decide(seller, 'Accept transfer', ['yes', 'no'])
        if acceptance_decision == 'yes':
            logger.debug('Seller accepts transfer')
            # TODO implement
        elif acceptance_decision == 'no':
            logger.debug('Seller does not accept transfer')
            environment.wait(self._timeout)
            environment.send_contract_transaction(self._mediator_contract, buyer, 'abort', trade_id)
        else:
            raise ProtocolExecutionError('Unhandled decision outcome')


ProtocolManager.register('SmartJudge-FairSwap', SmartJudge)
