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
from typing import Any, List, Optional, Union, cast

from hexbytes.main import HexBytes
from jinja2 import Template
from web3 import Web3

from bdtsim.account import Account
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, ProtocolInitializationError, ProtocolExecutionError
from bdtsim.protocol_path import ProtocolPath
from . import merkle, encoding


logger = logging.getLogger(__name__)


class FairSwap(Protocol):
    SINGLE_USE_CONTRACT_TEMPLATE_FILE = 'FairFileSale.tpl.sol'
    REUSABLE_CONTRACT_FILE = 'FairFileSale-reusable.sol'
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

        self.slices_count = int(slices_count)
        if self.slices_count < 1:
            raise ProtocolInitializationError('n must be an int >= 1')

        if not math.log2(self.slices_count).is_integer():
            raise ProtocolInitializationError('slice_count must be a power of 2')
        self.merkle_tree_depth = int(math.log2(self.slices_count)) + 1

        self.timeout = int(timeout)

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
        with open(self.contract_path(__file__, FairSwap.SINGLE_USE_CONTRACT_TEMPLATE_FILE)) as f:
            contract_template = Template(f.read())

        contract_code_rendered = contract_template.render(
            merkle_tree_depth=self.merkle_tree_depth,
            slice_length=slice_length,
            slices_count=self.slices_count,
            timeout=self.timeout,
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
        slice_length = int(data_provider.data_size / self.slices_count)
        if slice_length % 32 > 0:
            raise ProtocolExecutionError('A slice must have a multiple of 32 as length.'
                                         ' Configured for using %d slices,'
                                         ' therefore data must have a multiple of %d as length' % (
                                            self.slices_count,
                                            self.slices_count * 32
                                         ))

        plain_data = data_provider.file_pointer.read()
        plain_merkle_tree = merkle.from_bytes(plain_data, self.slices_count)
        key = self.generate_bytes(32, 1337)

        # === 1a: Seller: encrypt file for transmission
        encryption_decision = protocol_path.decide(
            seller, 'File Encryption/Transfer', ['expected', 'completely different', 'leaf forgery', 'hash forgery']
        )
        if encryption_decision == 'expected':
            encrypted_merkle_tree = encoding.encode(plain_merkle_tree, key)
        elif encryption_decision == 'completely different':
            encrypted_merkle_tree = encoding.encode(
                merkle.from_bytes(self.generate_bytes(data_provider.data_size), self.slices_count),
                key
            )
        elif encryption_decision == 'leaf forgery' or encryption_decision == 'hash forgery':
            # extract correct plain data
            plain_leaves_data = [leaf.data for leaf in plain_merkle_tree.leaves]
            plain_digests = plain_merkle_tree.digests_pack

            # forge first leaf
            plain_leaves_data[0] = b'\x00' * len(plain_leaves_data[0])

            if encryption_decision == 'hash forgery':
                plain_digests[0] = merkle.MerkleTreeNode(
                    merkle.MerkleTreeLeaf(plain_leaves_data[0]),
                    merkle.MerkleTreeLeaf(plain_leaves_data[1])
                ).digest

            encrypted_leaves_data = [encoding.crypt(data, i, key) for i, data in enumerate(plain_leaves_data)]
            encrypted_digests = [
                encoding.crypt(data, 2 * len(plain_leaves_data) + i, key) for i, data in enumerate(plain_digests)
            ]

            encrypted_merkle_tree = merkle.from_leaves([merkle.MerkleTreeLeaf(x) for x in encrypted_leaves_data]
                                                       + [merkle.MerkleTreeHashLeaf(x) for x in encrypted_digests]
                                                       + [merkle.MerkleTreeHashLeaf(encoding.B032)])
        else:
            raise NotImplementedError()

        # === 1b: Seller: deploy smart contract
        deployment_decision = protocol_path.decide(seller, 'Contract Deployment',
                                                   ['as expected by buyer', 'commitment to wrong key',
                                                    'unexpected file root hash', 'incorrect ciphertext root hash'])
        if deployment_decision == 'as expected by buyer':
            transfer_plain_root_hash = plain_merkle_tree.digest
            transfer_ciphertext_root_hash = encrypted_merkle_tree.digest
            transfer_key = key
        elif deployment_decision == 'commitment to wrong key':
            transfer_plain_root_hash = plain_merkle_tree.digest
            transfer_ciphertext_root_hash = encrypted_merkle_tree.digest
            transfer_key = self.generate_bytes(32, avoid=key)
        elif deployment_decision == 'unexpected file root hash':
            transfer_plain_root_hash = self.generate_bytes(32, avoid=plain_merkle_tree.digest)
            transfer_ciphertext_root_hash = encrypted_merkle_tree.digest
            transfer_key = key
        elif deployment_decision == 'incorrect ciphertext root hash':
            transfer_plain_root_hash = plain_merkle_tree.digest
            transfer_ciphertext_root_hash = self.generate_bytes(32, avoid=encrypted_merkle_tree.digest)
            transfer_key = key
        else:
            raise NotImplementedError()

        # init FairSwap protocol (deploy contract in single use case/ call init method in reusable case)
        self.smart_contract_init(
            environment=environment,
            seller=seller,
            buyer=buyer,
            price=price,
            slice_length=int(slice_length / 32),
            file_root_hash=transfer_plain_root_hash,
            ciphertext_root_hash=transfer_ciphertext_root_hash,
            key_hash=Web3.solidityKeccak(['bytes32'], [transfer_key])
        )

        # === 2: Buyer: Accept Contract/Pay Price ===
        if (plain_merkle_tree.digest == transfer_plain_root_hash
                and encrypted_merkle_tree.digest == transfer_ciphertext_root_hash):
            acceptance_decision = protocol_path.decide(buyer, 'Accept', variants=['yes', 'leave'])
            if acceptance_decision == 'yes':
                self.smart_contract_accept(environment, seller, buyer, transfer_plain_root_hash, price)
            elif acceptance_decision == 'leave':
                return
            else:
                raise NotImplementedError()
        else:
            return

        # === 3: Seller: Reveal key ===
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', ['yes', 'leave'])
        if key_revelation_decision == 'yes':
            self.smart_contract_reveal_key(environment, seller, buyer, transfer_plain_root_hash, transfer_key)
        elif key_revelation_decision == 'leave':
            logger.debug('Seller: Leaving without Key Revelation')
            if protocol_path.decide(buyer, 'Refund', variants=['yes', 'no']) == 'yes':
                logger.debug('Buyer: Waiting for timeout to request refund')
                environment.wait(self.timeout + 1)
                self.smart_contract_refund(environment, seller, buyer, transfer_plain_root_hash, buyer)
            return
        else:
            raise NotImplementedError()

        # === 4: Buyer: Send Ok/Complain/Leave
        root_hash_enc = encrypted_merkle_tree.leaves[-2].data
        if encoding.crypt(root_hash_enc, 3 * self.slices_count - 2, transfer_key) != plain_merkle_tree.digest:
            if protocol_path.decide(buyer, 'complain about root', ['yes']) == 'yes':
                logger.debug('Buyer: Complaining about incorrect file root hash')
                root_hash_leaf = encrypted_merkle_tree.leaves[-2]
                proof = encrypted_merkle_tree.get_proof(root_hash_leaf)
                self.smart_contract_complain_about_root(environment, seller, buyer, transfer_plain_root_hash,
                                                        root_hash_leaf.data, proof)
                return
        else:
            decrypted_merkle_tree, errors = encoding.decode(encrypted_merkle_tree, transfer_key)
            if len(errors) == 0:
                if protocol_path.decide(buyer, 'Confirm', variants=['yes', 'leave'],
                                        honest_variants=['yes', 'leave']) == 'yes':
                    self.smart_contract_no_complain(environment, seller, buyer, transfer_plain_root_hash)
                    return
            elif isinstance(errors[-1], encoding.LeafDigestMismatchError):
                if protocol_path.decide(buyer, 'Complain about Leaf', ['yes']) == 'yes':
                    error: encoding.NodeDigestMismatchError = errors[-1]
                    self.smart_contract_complain_about_leaf(
                        environment=environment,
                        seller=seller,
                        buyer=buyer,
                        file_root_hash=transfer_plain_root_hash,
                        error=error,
                        proof_out=encrypted_merkle_tree.get_proof(error.out),
                        proof_in1=encrypted_merkle_tree.get_proof(error.in1)
                    )
                    return
            else:
                if protocol_path.decide(buyer, 'Complain about Node', ['yes']) == 'yes':
                    error = errors[-1]
                    self.smart_contract_complain_about_node(
                        environment=environment,
                        seller=seller,
                        buyer=buyer,
                        file_root_hash=transfer_plain_root_hash,
                        error=error,
                        proof_out=encrypted_merkle_tree.get_proof(error.out),
                        proof_in1=encrypted_merkle_tree.get_proof(error.in1)
                    )
                    return

        # === 5: Seller: Finalize (when Buyer leaves in 4)
        if protocol_path.decide(seller, 'Request Payout', variants=['yes', 'no'],
                                honest_variants=['yes', 'no']) == 'yes':
            environment.wait(self.timeout + 1)
            self.smart_contract_refund(environment, seller, buyer, transfer_plain_root_hash, seller)

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

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, price: int,
                            slice_length: int, file_root_hash: bytes, ciphertext_root_hash: bytes,
                            key_hash: bytes) -> None:
        environment.deploy_contract(seller, self._get_contract(
            buyer=buyer,
            price=price,
            slice_length=slice_length,
            file_root_hash=file_root_hash,
            ciphertext_root_hash=ciphertext_root_hash,
            key_hash=key_hash
        ))

    @staticmethod
    def smart_contract_accept(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                              price: int) -> None:
        environment.send_contract_transaction(buyer, 'accept', value=price)

    @staticmethod
    def smart_contract_reveal_key(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                                  key: bytes) -> None:
        environment.send_contract_transaction(seller, 'revealKey', key)

    @staticmethod
    def smart_contract_refund(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                              beneficiary: Account) -> None:
        environment.send_contract_transaction(beneficiary, 'refund')

    @staticmethod
    def smart_contract_no_complain(environment: Environment, seller: Account, buyer: Account,
                                   file_root_hash: bytes) -> None:
        environment.send_contract_transaction(buyer, 'noComplain')

    @staticmethod
    def smart_contract_complain_about_root(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, witness: bytes, proof: List[bytes]) -> None:
        environment.send_contract_transaction(buyer, 'complainAboutRoot', witness, proof)

    @staticmethod
    def smart_contract_complain_about_leaf(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, error: encoding.NodeDigestMismatchError,
                                           proof_out: List[bytes], proof_in1: List[bytes]) -> None:
        environment.send_contract_transaction(
            buyer,
            'complainAboutLeaf',
            error.index_out,
            error.index_in,
            error.out.data,
            error.in1.data_as_list(),
            error.in2.data_as_list(),
            proof_out,
            proof_in1
        )

    @staticmethod
    def smart_contract_complain_about_node(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, error: encoding.NodeDigestMismatchError,
                                           proof_out: List[bytes], proof_in1: List[bytes]) -> None:
        environment.send_contract_transaction(
            buyer,
            'complainAboutNode',
            error.index_out,
            error.index_in,
            error.out.data,
            error.in1.data,
            error.in2.data,
            proof_out,
            proof_in1
        )


class FairSwapReusable(FairSwap):
    def _get_reusable_contract(self) -> SolidityContract:
        with open(self.contract_path(__file__, FairSwap.REUSABLE_CONTRACT_FILE)) as f:
            contract_code = f.read()
        return SolidityContract(FairSwap.CONTRACT_NAME, contract_code=contract_code)

    @staticmethod
    def get_session_id(seller: Account, buyer: Account, file_root_hash: bytes) -> bytes:
        return cast(bytes, Web3.solidityKeccak(
            ['address', 'address', 'bytes32'],
            [seller.wallet_address, buyer.wallet_address, file_root_hash]
        ))

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        logger.debug('Deploying reusable smart contract...')
        environment.deploy_contract(operator, self._get_reusable_contract())

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, price: int,
                            slice_length: int, file_root_hash: bytes, ciphertext_root_hash: bytes,
                            key_hash: bytes) -> None:
        environment.send_contract_transaction(
            seller,
            'init',
            buyer.wallet_address,
            self.merkle_tree_depth,
            slice_length,
            self.slices_count,
            self.timeout,
            price,
            key_hash,
            ciphertext_root_hash,
            file_root_hash
        )

    @staticmethod
    def smart_contract_accept(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                              price: int) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(buyer, 'accept', session_id, value=price)

    @staticmethod
    def smart_contract_reveal_key(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                                  key: bytes) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(seller, 'revealKey', session_id, key)

    @staticmethod
    def smart_contract_refund(environment: Environment, seller: Account, buyer: Account, file_root_hash: bytes,
                              beneficiary: Account) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(beneficiary, 'refund', session_id)

    @staticmethod
    def smart_contract_no_complain(environment: Environment, seller: Account, buyer: Account,
                                   file_root_hash: bytes) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(buyer, 'noComplain', session_id)

    @staticmethod
    def smart_contract_complain_about_root(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, witness: bytes, proof: List[bytes]) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(buyer, 'complainAboutRoot', session_id, witness, proof)

    @staticmethod
    def smart_contract_complain_about_leaf(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, error: encoding.NodeDigestMismatchError,
                                           proof_out: List[bytes], proof_in1: List[bytes]) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(
            buyer,
            'complainAboutLeaf',
            session_id,
            error.index_out,
            error.index_in,
            error.out.data,
            error.in1.data_as_list(),
            error.in2.data_as_list(),
            proof_out,
            proof_in1
        )

    @staticmethod
    def smart_contract_complain_about_node(environment: Environment, seller: Account, buyer: Account,
                                           file_root_hash: bytes, error: encoding.NodeDigestMismatchError,
                                           proof_out: List[bytes], proof_in1: List[bytes]) -> None:
        session_id = FairSwapReusable.get_session_id(seller, buyer, file_root_hash)
        environment.send_contract_transaction(
            buyer,
            'complainAboutNode',
            session_id,
            error.index_out,
            error.index_in,
            error.out.data,
            error.in1.data,
            error.in2.data,
            proof_out,
            proof_in1
        )


ProtocolManager.register('FairSwap', FairSwap)
ProtocolManager.register('FairSwap-Reusable', FairSwapReusable)
