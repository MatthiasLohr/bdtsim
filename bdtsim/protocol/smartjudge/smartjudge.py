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
import os
from typing import Any

from bdtsim.account import Account
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class SmartJudge(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._mediator_contract = SolidityContract(
            contract_name='Mediator',
            contract_file=self.contract_path(__file__, 'mediator.sol'),
            solc_version='0.4.26'
        )

        self._verifier_contract = SolidityContract(
            contract_name='fileSale',
            contract_file=self.contract_path(__file__, 'verifier-fairswap.sol'),
            solc_version='0.4.26',
            compiler_kwargs={
                'import_remappings': '=%s' % os.path.dirname(self.contract_path(__file__, 'verifier-fairswap.sol'))
            }
        )

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        environment.deploy_contract(operator, self._mediator_contract)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        pass


ProtocolManager.register('SmartJudge-FairSwap', SmartJudge)
