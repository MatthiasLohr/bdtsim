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
from typing import Optional

from eth_utils.crypto import keccak
from jinja2 import Template
from web3 import Web3

from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.contract import SolidityContract
from bdtsim.environment import Environment
from bdtsim.participant import Participant
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class FairSwap(Protocol):
    def __init__(self, contract_template_file: str, depth: Optional[int] = 16, length: Optional[int] = 16,

                 n: Optional[int] = 16, key: Optional[bytes] = None, ciphertext_root: Optional[str] = None,
                 file_root: Optional[str] = None) -> None:

        super(FairSwap, self).__init__()
        self._contract_template_file = contract_template_file

        self._depth = depth
        self._length = length
        self._n = n

        if key is not None:
            self._key = key
        else:
            self._key = os.urandom(32)

        self._ciphertext_root = ciphertext_root or '0x' + keccak(b'cipher').hex()
        self._file_root = file_root or '0x' + keccak(b'plain').hex()

    def get_contract(self, receiver: Participant, price: int) -> SolidityContract:
        contract_template_path = self.contract_path(__file__, self._contract_template_file)
        with open(contract_template_path, 'r') as f:
            contract_code = f.read()
        contract_template = Template(contract_code)
        contract_rendered = contract_template.render(
            depth=self._depth,
            length=self._length,
            n=self._n,
            receiver=receiver.wallet_address,
            price=price,
            key_commit=Web3.solidityKeccak(['bytes32'], [self._key]).hex(),
            ciphertext_root=self._ciphertext_root,
            file_root=self._file_root
        )
        return SolidityContract('FileSale', contract_code=contract_rendered)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, seller: Participant, buyer: Participant,
                price: int = 1000000000) -> None:

        logger.debug('Protocol Start')

        # seller deploys contract containing commitment hashes
        if protocol_path.decide(seller, description='Contract Deployment').is_honest():
            logger.debug('Seller: Initializing contract with CORRECT data')
            # TODO implement
        else:
            logger.debug('Seller: Initializing contract with INCORRECT data')
            # TODO implement

        # buyer accepts contract
        if protocol_path.decide(buyer, description='Acceptance').is_honest():
            logger.debug('Buyer: Accepting transfer')
            # TODO implement
            key_revelation_decision = protocol_path.decide(seller, variants=3, description='Key Revelation')
            if key_revelation_decision.is_honest():
                logger.debug('Seller: Sending correct key')
                pass  # TODO implement
            elif key_revelation_decision.is_variant(2):
                logger.debug('Seller: Sending wrong key')
                pass  # TODO implement
            elif key_revelation_decision.is_variant(3):
                logger.debug('Seller: Sending no key')
                pass  # TODO implement
        else:
            logger.debug('Buyer: Not accepting transfer')
            # not doing anything - protocol ends

        logger.debug('Protocol End')


ProtocolManager.register('FairSwap-FileSale', FairSwap, 'FairFileSale.tpl.sol')
