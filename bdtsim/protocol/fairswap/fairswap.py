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
import math
import random
from typing import Optional, Union

from eth_utils.crypto import keccak
from hexbytes.main import HexBytes
from jinja2 import Template
from web3 import Web3

from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.participant import Participant
from bdtsim.protocol_path import ProtocolPath
from bdtsim.util import merkle_tree
from bdtsim.util.xor import xor_crypt


logger = logging.getLogger(__name__)


class FairSwap(Protocol):
    """FairSwap-FileSale protocol execution plan"""
    def __init__(self, contract_template_file: str, n: int = 16, key: Optional[bytes] = None,
                 fake_file_root_hash: Optional[bytes] = None,
                 fake_ciphertext_root_hash: Optional[bytes] = None) -> None:
        """
        Args:
            contract_template_file (str): Name of the file containing the contract template (rendered using Jinja2)
            n (int): number of slices in which the data is to be split
            key (bytes): encryption key
            fake_file_root_hash (bytes): fake (wrong) file root hash, used when cheating
            fake_ciphertext_root_hash (bytes): fake (wrong) ciphertext root hash, used when cheating
        """
        super(FairSwap, self).__init__()
        self._contract_template_file = contract_template_file

        self._n = int(n)

        self._key = key or self.generate_bytes(length=32, seed=1337)
        self._fake_file_root_hash = fake_file_root_hash
        self._fake_ciphertext_root_hash = fake_ciphertext_root_hash

    def get_contract(self, receiver: Participant, price: int, length: int, file_root_hash: bytes,
                     ciphertext_root_hash: bytes) -> SolidityContract:
        """
        Args:
            receiver (Participant: Who wants to receive the data and therefore has to pay
            price (int): price for the data purchase
            length (int): Length of one data slice
            file_root_hash (bytes):
            ciphertext_root_hash (bytes):
        Returns:
            SolidityContract: prepared contract for deployment
        """
        contract_template_path = self.contract_path(__file__, self._contract_template_file)

        with open(contract_template_path, 'r') as f:
            contract_code = f.read()

        contract_template = Template(contract_code)

        contract_rendered = contract_template.render(
            n=self._n,
            depth=math.ceil(math.log2(self._n)),
            length=length,
            receiver=receiver.wallet_address,
            price=price,
            key_commitment=self.hex(Web3.solidityKeccak(['bytes32'], [self._key])),
            file_root_hash=self.hex(file_root_hash),
            ciphertext_root_hash=self.hex(ciphertext_root_hash)
        )

        return SolidityContract('FileSale', contract_code=contract_rendered)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Participant, buyer: Participant, price: int = 1000000000) -> None:

        if data_provider.data_size % self._n:
            raise RuntimeError('Can not divide data of length %d equally in %d slices' % (
                data_provider.data_size,
                self._n
            ))

        logger.debug('Protocol Start')

        slice_length = data_provider.data_size // self._n
        file_merkle_tree = merkle_tree.from_file(data_provider.file_pointer, self._n)
        ciphertext_merkle_tree = self.encrypt_merkle_tree(file_merkle_tree, self._key)

        communicated_file_root_hash = None
        communicated_ciphertext_root_hash = None

        # Seller: Deploy contract with file/ciphertext root hashes and key commitment
        deployment_decision = protocol_path.decide(seller, variants=4, description='Contract Deployment')
        if deployment_decision.is_honest():
            logger.debug('Seller: Preparing contract with correct hashes')
            communicated_file_root_hash = file_merkle_tree.digest(keccak)
            communicated_ciphertext_root_hash = ciphertext_merkle_tree.digest(keccak)
        elif deployment_decision.is_variant(2):
            logger.debug('Seller: Preparing contract with incorrect file root hash')
            communicated_file_root_hash = self.generate_bytes(length=32, seed=1338,
                                                              avoid=file_merkle_tree.digest(keccak))
            communicated_ciphertext_root_hash = ciphertext_merkle_tree.digest(keccak)
        elif deployment_decision.is_variant(3):
            logger.debug('Seller: Preparing contract with incorrect ciphertext root hash')
            communicated_file_root_hash = file_merkle_tree.digest(keccak)
            communicated_ciphertext_root_hash = self.generate_bytes(length=32, seed=1339,
                                                                    avoid=ciphertext_merkle_tree.digest(keccak))
        elif deployment_decision.is_variant(4):
            logger.debug('Seller: Preparing contract with incorrect file and incorrect ciphertext root hash')
            communicated_file_root_hash = self.generate_bytes(length=32, seed=1338,
                                                              avoid=file_merkle_tree.digest(keccak))
            communicated_ciphertext_root_hash = self.generate_bytes(length=32, seed=1339,
                                                                    avoid=ciphertext_merkle_tree.digest(keccak))

        if communicated_file_root_hash is None:
            raise RuntimeError('Cannot work with empty communicated_file_root_hash')
        if communicated_ciphertext_root_hash is None:
            raise RuntimeError('Cannot work with empty communicated_ciphertext_root_hash')

        environment.deploy_contract(seller, self.get_contract(
            receiver=buyer,
            price=price,
            length=slice_length,
            file_root_hash=communicated_file_root_hash,
            ciphertext_root_hash=communicated_ciphertext_root_hash
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

    @staticmethod
    def generate_bytes(length: int = 32, seed: Optional[int] = None, avoid: Optional[bytes] = None) -> bytes:
        if seed is not None:
            random.seed(seed)
        tmp = avoid
        while tmp is None or tmp == avoid:
            tmp = bytearray(random.getrandbits(8) for _ in range(length))
        return tmp

    @staticmethod
    def encrypt_merkle_tree(plain: merkle_tree.MerkleTreeNode, key: bytes) -> merkle_tree.MerkleTreeNode:
        leaves_encrypted = [xor_crypt(l, key) for l in plain.leaves]
        digests_encrypted = [xor_crypt(d, key) for d in plain.digests_dfs(keccak)]
        return merkle_tree.from_bytes_list(leaves_encrypted + digests_encrypted)


ProtocolManager.register('FairSwap-FileSale', FairSwap, 'FairFileSale.tpl.sol')
