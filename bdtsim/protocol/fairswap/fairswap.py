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
from typing import Any, Optional, Union

from eth_utils.crypto import keccak
from hexbytes.main import HexBytes
from jinja2 import Template

from bdtsim.account import Account
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, ProtocolInitializationError, ProtocolExecutionError
from bdtsim.protocol_path import ProtocolPath
from bdtsim.util.xor import xor_crypt
from . import encryption, merkle


logger = logging.getLogger(__name__)


class FairSwap(Protocol):
    CONTRACT_TEMPLATE_FILE = 'FairFileSale.tpl.sol'
    CONTRACT_NAME = 'FileSale'

    def __init__(self, slices_count: int = 8, timeout: int = 600, *args: Any, **kwargs: Any) -> None:
        """
        Args:
            slices_count (int): number of slices in which the data is to be split
            timeout (int): Timeout in seconds before refund can be used
            *args (Any): Additional arguments
            **kwargs (Any): Additional keyword arguments
        """
        super(FairSwap, self).__init__(*args, **kwargs)

        self._slices_count = int(slices_count)
        if self._slices_count < 1:
            raise ProtocolInitializationError('n must be an int >= 1')

        if not math.log2(self._slices_count).is_integer():
            raise ProtocolInitializationError('slice_count must be a power of 2')
        self._merkle_tree_depth = int(math.log2(self._slices_count)) + 1

        self._timeout = int(timeout)

    def _get_contract(self, buyer: Account, price: int, slice_length: int, file_root_hash: bytes,
                      ciphertext_root_hash: bytes, key_hash: bytes) -> SolidityContract:
        """
        Args:
            buyer (Account): Account which has to pay and will receive the data
            price (int): Price of the data to be traded in Wei
            slice_length (int): length of a data slice, must be a multiple of 32
            file_root_hash (bytes): bytes32 root hash of the plain file's merkle tree
            ciphertext_root_hash (bytes): bytes32 root has of the encrypted file's merkle tree
            key_hash (bytes): bytes32 keccak hash of key to be used

        Returns:
            SolidityContract: Actual smart contract to be deployed with pre-filled values
        """
        with open(self.contract_path(__file__, FairSwap.CONTRACT_TEMPLATE_FILE)) as f:
            contract_template = Template(f.read())

        contract_code_rendered = contract_template.render(
            merkle_tree_depth=self._merkle_tree_depth,
            slice_length=slice_length,
            slices_count=self._slices_count,
            timeout=self._timeout,
            receiver=buyer.wallet_address,
            price=price,
            key_commitment=self.hex(key_hash),
            ciphertext_root_hash=self.hex(ciphertext_root_hash),
            file_root_hash=self.hex(file_root_hash)
        )

        return SolidityContract(FairSwap.CONTRACT_NAME, contract_code=contract_code_rendered)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        """Execute a file transfer using the FairSwap protocol / FileSale contract.

        Args:
            protocol_path (ProtocolPath):
            environment (Environment):
            data_provider (DataProvider):
            seller (Account):
            buyer (Account):
            price (int):

        Returns:
            None:
        """
        # initial assignments and checks
        slice_length = int(data_provider.data_size / self._slices_count)
        if slice_length % 32 > 0:
            raise ProtocolExecutionError('A slice must have a multiple of 32 as length.'
                                         ' Configured for using %d slices,'
                                         ' therefore data must have a multiple of %d as length' % (
                                             self._slices_count,
                                             self._slices_count * 32
                                         ))

        real_plain_data = data_provider.file_pointer.read()
        real_key = self.generate_bytes(32, 1337)

        # === 1a: Seller: encrypt file for transmission
        encrypt_decision = protocol_path.decide(seller, 'File Encryption/Send', [
            'correct', 'fake data', 'hash forgery', 'leaf forgery'
        ])
        if encrypt_decision == 'correct':
            transfer_plain_merkle_tree = merkle.from_bytes(real_plain_data)
            transfer_ciphertext_merkle_tree = encryption.encrypt_merkle_tree(transfer_plain_merkle_tree, real_key)
        elif encrypt_decision == 'fake data':
            fake_plain_data = real_plain_data[:-1] + (real_plain_data[-1] ^ 1).to_bytes(1, 'little')
            transfer_plain_merkle_tree = merkle.from_bytes(fake_plain_data)
            transfer_ciphertext_merkle_tree = encryption.encrypt_merkle_tree(transfer_plain_merkle_tree, real_key)
        elif encrypt_decision == 'leaf forgery':
            transfer_plain_merkle_tree = merkle.from_bytes(real_plain_data)
            # manually crypt and exchange leaf value
            leaves_encrypted = [xor_crypt(bytes(leaf), real_key) for leaf in transfer_plain_merkle_tree.leaves]
            digests_encrypted = [xor_crypt(digest, real_key) for digest in transfer_plain_merkle_tree.digests_pack]
            # modify leaf data
            leaves_encrypted[0] = b'0' * len(leaves_encrypted[0])
            # build encrypted merkle tree
            transfer_ciphertext_merkle_tree = merkle.from_list(leaves_encrypted + digests_encrypted)
        elif encrypt_decision == 'hash forgery':
            transfer_plain_merkle_tree = merkle.from_bytes(real_plain_data)
            # manually crypt and exchange leaf value
            leaves_encrypted = [xor_crypt(bytes(leaf), real_key) for leaf in transfer_plain_merkle_tree.leaves]
            digests_encrypted = [xor_crypt(digest, real_key) for digest in transfer_plain_merkle_tree.digests_pack]
            # modify two leaves and according hash
            leaves_encrypted[0] = b'0' * len(leaves_encrypted[0])
            leaves_encrypted[1] = b'0' * len(leaves_encrypted[1])
            digests_encrypted[0] = xor_crypt(keccak(leaves_encrypted[0] + leaves_encrypted[1]), real_key)
            # build encrypted merkle tree
            transfer_ciphertext_merkle_tree = merkle.from_list(leaves_encrypted + digests_encrypted)
        else:
            raise ProtocolExecutionError('Unsupported decision outcome: %s' % encrypt_decision.outcome)

        # === 1b: Seller: deploy smart contract
        deployment_decision = protocol_path.decide(seller, 'Contract Deployment', [
            'correct', 'commitment to wrong key', 'incorrect plain root hash', 'incorrect ciphertext root hash'
        ])
        if deployment_decision == 'correct':
            transfer_plain_root_hash = transfer_plain_merkle_tree.digest
            transfer_ciphertext_root_hash = transfer_ciphertext_merkle_tree.digest
            transfer_key = real_key
        elif deployment_decision == 'commitment to wrong key':
            transfer_plain_root_hash = transfer_plain_merkle_tree.digest
            transfer_ciphertext_root_hash = transfer_ciphertext_merkle_tree.digest
            transfer_key = self.generate_bytes(32, 1338, avoid=real_key)
        elif deployment_decision == 'incorrect plain root hash':
            transfer_plain_root_hash = self.generate_bytes(32, 1337, avoid=transfer_plain_merkle_tree.digest)
            transfer_ciphertext_root_hash = transfer_ciphertext_merkle_tree.digest
            transfer_key = real_key
        elif deployment_decision == 'incorrect ciphertext root hash':
            transfer_plain_root_hash = transfer_plain_merkle_tree.digest
            transfer_ciphertext_root_hash = self.generate_bytes(32, 1337, avoid=transfer_ciphertext_merkle_tree.digest)
            transfer_key = real_key
        else:
            raise ProtocolExecutionError('Unsupported decision outcome: %s' % deployment_decision.outcome)

        environment.deploy_contract(seller, self._get_contract(
            buyer=buyer,
            price=price,
            slice_length=slice_length,
            file_root_hash=transfer_plain_root_hash,
            ciphertext_root_hash=transfer_ciphertext_root_hash,
            key_hash=keccak(transfer_key)
        ))

        # === 2: Buyer: Accept Contract/Pay Price ===
        if (transfer_plain_merkle_tree.digest == transfer_plain_root_hash
                and transfer_ciphertext_merkle_tree.digest == transfer_ciphertext_root_hash):
            acceptance_decision = protocol_path.decide(buyer, 'Accept', variants=['yes', 'leave'])
            if acceptance_decision == 'yes':
                environment.send_contract_transaction(buyer, 'accept', value=price)
            elif acceptance_decision == 'leave':
                return
            else:
                raise ProtocolExecutionError('Unsupported decision outcome: %s' % acceptance_decision.outcome)
        else:
            return

        # === 3: Seller: Reveal key ===
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', variants=['correct', 'leave'])
        if key_revelation_decision == 'correct':
            environment.send_contract_transaction(seller, 'revealKey', transfer_key)
            print('worked')
        elif key_revelation_decision == 'leave':
            pass
        else:
            raise ProtocolExecutionError('Unsupported decision outcome: %s' % key_revelation_decision.outcome)

        # === 4: Buyer: Send Ok/Complain/Leave
        # TODO implement

        # === 5: Seller: Finalize (when Buyer leaves in 4)
        # TODO implement

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
            tmp = bytes(bytearray(random.getrandbits(8) for _ in range(length)))
        return tmp


ProtocolManager.register('FairSwap-FileSale', FairSwap)
