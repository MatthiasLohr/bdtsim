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
from typing import Optional, Union

from hexbytes.main import HexBytes
from jinja2 import Template
from web3 import Web3

from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.participant import Participant
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class FairSwap(Protocol):
    """FairSwap-FileSale protocol execution plan"""
    def __init__(self, contract_template_file: str, depth: Optional[int] = 16, length: Optional[int] = 16,
                 n: Optional[int] = 16, correct_key: Optional[bytes] = None,
                 incorrect_key: Optional[bytes] = None,
                 correct_file_root_hash: Optional[bytes] = None, incorrect_file_root_hash: Optional[bytes] = None,
                 correct_ciphertext_root_hash: Optional[bytes] = None,
                 incorrect_ciphertext_root_hash: Optional[bytes] = None) -> None:
        """
        Args:
            contract_template_file (str): Name of the file containing the contract template (rendered using Jinja2)
            depth (int):
            length (int):
            n (int):
            correct_key (bytes):
            incorrect_key (bytes):
            correct_file_root_hash (bytes):
            incorrect_file_root_hash (bytes):
            correct_ciphertext_root_hash (bytes):
            incorrect_ciphertext_root_hash (bytes):
        """
        super(FairSwap, self).__init__()
        self._contract_template_file = contract_template_file

        self._depth = depth
        self._length = length
        self._n = n

        self._correct_key = correct_key or bytearray.fromhex(
                '14d60b7868da0fbc6ac34fc9a7f93476699b7cfb416a5e15c33d511228711cb0'
            )
        self._incorrect_key = incorrect_key or bytearray.fromhex(
                'eb43694f327f8deb06561eb95135ff87e445ca771ee39f115862df9654b49246'
            )
        self._correct_file_root_hash = correct_file_root_hash or bytearray.fromhex(
                'bf7315a07f38ba7b06b53b8439455f91228fe787f5288dfcb9e056a015b3f8d3'
            )
        self._incorrect_file_root_hash = incorrect_file_root_hash or bytearray.fromhex(
                '11f70f80685f9d3ab0dfae449714e45e47a1f9ec36310c803486523a6f0fdd10'
            )
        self._correct_ciphertext_root_hash = correct_ciphertext_root_hash or bytearray.fromhex(
                'ac092cefe8702fffe2f8e1ac6589af9a8ffe426f27d8a1722d2d3d7099067b7b'
            )
        self._incorrect_ciphertext_root_hash = incorrect_ciphertext_root_hash or bytearray.fromhex(
                '52a6f76d34712433e5fa96ad0f8430bbaafca33d3e0dbed771cd8096f0621c74'
            )

    def get_contract(self, receiver: Participant, price: int, key: bytes, file_root_hash: bytes,
                     ciphertext_root_hash: bytes) -> SolidityContract:
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
            key_commitment=self.hex(Web3.solidityKeccak(['bytes32'], [key])),
            file_root_hash=self.hex(file_root_hash),
            ciphertext_root_hash=self.hex(ciphertext_root_hash)
        )
        return SolidityContract('FileSale', contract_code=contract_rendered)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Participant, buyer: Participant, price: int = 1000000000) -> None:

        logger.debug('Protocol Start')

        # Seller: Deploy contract with file/ciphertext root hashes and key commitment
        deployment_decision = protocol_path.decide(seller, variants=4, description='Contract Deployment')
        if deployment_decision.is_honest():
            logger.debug('Seller: Deploying contract with correct hashes')
            environment.deploy_contract(seller, self.get_contract(
                receiver=buyer,
                price=price,
                key=self._correct_key,
                file_root_hash=self._correct_file_root_hash,
                ciphertext_root_hash=self._correct_ciphertext_root_hash
            ))
        elif deployment_decision.is_variant(2):
            logger.debug('Seller: Deploying contract incorrect file root hash')
            environment.deploy_contract(seller, self.get_contract(
                receiver=buyer,
                price=price,
                key=self._correct_key,
                file_root_hash=self._incorrect_file_root_hash,
                ciphertext_root_hash=self._correct_ciphertext_root_hash
            ))
        elif deployment_decision.is_variant(3):
            logger.debug('Seller: Deploying contract incorrect ciphertext root hash')
            environment.deploy_contract(seller, self.get_contract(
                receiver=buyer,
                price=price,
                key=self._correct_key,
                file_root_hash=self._correct_file_root_hash,
                ciphertext_root_hash=self._incorrect_ciphertext_root_hash
            ))
        elif deployment_decision.is_variant(4):
            logger.debug('Seller: Deploying contract incorrect file and ciphertext root hash')
            environment.deploy_contract(seller, self.get_contract(
                receiver=buyer,
                price=price,
                key=self._correct_key,
                file_root_hash=self._incorrect_file_root_hash,
                ciphertext_root_hash=self._incorrect_ciphertext_root_hash
            ))

        # buyer accepts contract
        if protocol_path.decide(buyer, description='Acceptance').is_honest():
            logger.debug('Buyer: Accepting transfer')
            environment.send_contract_transaction(buyer, 'accept', value=price)

            # seller reveals key (wrong key blocked by smart contract, so not implemented here)
            if protocol_path.decide(seller, description='Key Revelation').is_honest():
                logger.debug('Seller: Sending correct key')
                pass  # TODO implement
            else:
                logger.debug('Seller: Sending no key')
                # seller does nothing, buyer waits for timeout for refund
                pass  # TODO implement
        else:
            logger.debug('Buyer: Not accepting transfer')
            # not doing anything - protocol ends

        logger.debug('Protocol End')

    @staticmethod
    def hex(value: Union[HexBytes, bytes, bytearray]) -> str:
        if isinstance(value, HexBytes):
            return value.hex()
        elif isinstance(value, bytes):
            return '0x%s' % value.hex()
        elif isinstance(value, bytearray):
            return '0x%s' % value.hex()
        else:
            raise ValueError('Type not supported')


ProtocolManager.register('FairSwap-FileSale', FairSwap, 'FairFileSale.tpl.sol')
