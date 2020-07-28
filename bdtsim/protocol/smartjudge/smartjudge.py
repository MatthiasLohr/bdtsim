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
from typing import Any, Optional

from web3 import Web3

from bdtsim.account import Account
from bdtsim.contract import SolidityContractCollection
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, ProtocolInitializationError, ProtocolExecutionError
from bdtsim.protocol.fairswap import encoding, merkle
from bdtsim.protocol_path import ProtocolPath
from bdtsim.util.bytes import generate_bytes


logger = logging.getLogger(__name__)


class SmartJudge(Protocol):
    def __init__(self, worst_cast_cost: int = 1000000, security_deposit: int = 4000000, timeout: int = 86400,
                 on_chain_key_revelation: bool = True, slices_count: int = 8, slice_length: int = 32, *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._worst_case_cost = worst_cast_cost
        self._security_deposit = security_deposit
        self._timeout = timeout
        self._on_chain_key_revelation = on_chain_key_revelation
        self._slices_count = int(slices_count)
        if self._slices_count < 1:
            raise ProtocolInitializationError('n must be an int >= 1')

        if slice_length % 32 > 0:
            raise ProtocolExecutionError('A slice must have a multiple of 32 as length.'
                                         ' Configured for using %d slices,'
                                         ' therefore data must have a multiple of %d as length' % (
                                             self._slices_count,
                                             self._slices_count * 32
                                         ))
        self._slice_length = slice_length

        if not math.log2(self._slices_count).is_integer():
            raise ProtocolInitializationError('slice_count must be a power of 2')
        self._merkle_tree_depth = int(math.log2(self._slices_count)) + 1

        self._verifier_id: Optional[int] = None

        contract_collection = SolidityContractCollection(solc_version='0.4.26')
        contract_collection.add_contract_template_file(
            'Mediator',
            self.contract_path(__file__, 'mediator.tpl.sol'),
            {
                'security_deposit': security_deposit,
                'timeout': timeout
            },
            'mediator.sol'
        )
        contract_collection.add_contract_template_file(
            'fileSale',
            self.contract_path(__file__, 'verifier-fairswap.tpl.sol'),
            {
                'merkle_tree_depth': self._merkle_tree_depth,
                'slice_length': int(self._slice_length / 32),
                'slices_count': self._slices_count
            },
            'verifier-fairswap.sol'
        )

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

        self._verifier_id = None
        for event in environment.event_filter(self._mediator_contract, 'RegisteredVerifer', from_block=-1):
            self._verifier_id = int(event['args']['_id'])
            logger.debug('Verifier has ID %i' % self._verifier_id)
            break

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
        """Execute a file transfer using the SmartJudge Mediator Contract with FairSwap Verifier Contract

        Args:
            protocol_path (ProtocolPath):
            environment (Environment):
            data_provider (DataProvider):
            seller (Account):
            buyer (Account):
            price (int):

        Returns:

        """

        # === protocol initialization and value checking ===
        if self._slice_length != int(data_provider.data_size / self._slices_count):
            raise ProtocolExecutionError('Calculated slice length does not match'
                                         ' slice length defined on protocol level')

        plain_data = data_provider.file_pointer.read()
        plain_merkle_tree = merkle.from_bytes(plain_data, self._slices_count)
        key = generate_bytes(32, 1337)

        # === seller encrypts and offers data
        encryption_decision = protocol_path.decide(
            seller, 'File Encryption/Transfer', ['expected', 'completely different', 'leaf forgery', 'hash forgery']
        )
        if encryption_decision == 'expected':
            encrypted_merkle_tree = encoding.encode(plain_merkle_tree, key)
        elif encryption_decision == 'completely different':
            encrypted_merkle_tree = encoding.encode(
                merkle.from_bytes(generate_bytes(data_provider.data_size), self._slices_count),
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

        trade_conditions_hash = Web3.soliditySha3(
            ['bytes32', 'bytes32', 'bytes32'],
            [key, encrypted_merkle_tree.digest, plain_merkle_tree.digest]
        )

        # === seller communicates agreement
        trade_conditions_decision = protocol_path.decide(seller, 'Send correct trade conditions', ['yes', 'no'])
        if trade_conditions_decision == 'yes':
            transfer_trade_conditions_hash = trade_conditions_hash
        elif trade_conditions_decision == 'no':
            transfer_trade_conditions_hash = generate_bytes(len(trade_conditions_hash), avoid=trade_conditions_hash)
        else:
            raise NotImplementedError()

        # === buyer prepares new trade ===
        logger.debug('Buyer prepares new trade')
        agreement_hash = Web3.soliditySha3(['uint32', 'bytes32'], [self._verifier_id, transfer_trade_conditions_hash])
        agreement_decision = protocol_path.decide(buyer, 'Publish Agreement', ['correct', 'incorrect'])
        if agreement_decision == 'correct':
            transfer_agreement_hash = agreement_hash
        elif agreement_decision == 'incorrect':
            transfer_agreement_hash = generate_bytes(len(agreement_hash), avoid=agreement_hash)
        else:
            raise NotImplementedError()

        environment.send_contract_transaction(self._mediator_contract, buyer, 'create', transfer_agreement_hash,
                                              value=self._security_deposit * environment.gas_price)
        trade_id = None
        for event in environment.event_filter(self._mediator_contract, 'TradeID', from_block=-1):
            trade_id = event['args']['_id']
            logger.debug('Trade has id %i' % trade_id)
            break

        # === seller can accept transfer or leave ===
        if transfer_agreement_hash == agreement_hash:  # correct agreement
            acceptance_decision = protocol_path.decide(seller, 'Accept transfer', ['yes', 'no'])
            if acceptance_decision == 'yes':
                environment.send_contract_transaction(self._mediator_contract, seller, 'accept', trade_id,
                                                      value=self._security_deposit * environment.gas_price)
            elif acceptance_decision == 'no':
                logger.debug('Seller does not accept transfer, timeout')
                environment.wait(self._timeout)
                environment.send_contract_transaction(self._mediator_contract, buyer, 'abort', trade_id)
                return
            else:
                raise NotImplementedError()
        else:  # wrong agreement published by buyer
            logger.debug('Buyer tried to cheat, was detected by seller, buyer wants to get back funds')
            environment.wait(self._timeout)
            environment.send_contract_transaction(self._mediator_contract, buyer, 'abort', trade_id)
            return

        # === data transfer and secret revelation
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', ['correct', 'wrong', 'leave'])
        if key_revelation_decision == 'correct':
            transfer_key = key
        elif key_revelation_decision == 'wrong':
            transfer_key = generate_bytes(len(key), avoid=key)
        elif key_revelation_decision == 'leave':
            environment.wait(self._timeout)
            environment.send_contract_transaction(self._mediator_contract, buyer, 'timeout', trade_id)
            return
        else:
            raise NotImplementedError()

        if self._on_chain_key_revelation:
            environment.send_contract_transaction(self._mediator_contract, seller, 'reveal', trade_id, transfer_key)
        else:
            pass  # key revelation is done off-chain

        # === buyer confirms/contests correct transfer ===
        root_hash_enc = encrypted_merkle_tree.leaves[-2].data
        if encoding.crypt(root_hash_enc, 3 * self._slices_count - 2, transfer_key) != plain_merkle_tree.digest:
            if protocol_path.decide(buyer, 'complain about root', ['yes']) == 'yes':
                logger.debug('Buyer: Complaining about incorrect file root hash')
                root_hash_leaf = encrypted_merkle_tree.leaves[-2]
                proof = encrypted_merkle_tree.get_proof(root_hash_leaf)
                environment.send_contract_transaction(self._verifier_contract, buyer, 'complainAboutRoot',
                                                      trade_id, root_hash_leaf.data, proof)
                return
        else:
            decrypted_merkle_tree, errors = encoding.decode(encrypted_merkle_tree, transfer_key)
            if len(errors) == 0:
                confirmation_decision = protocol_path.decide(buyer, 'Send Confirmation?', ['yes', 'no'])
                if confirmation_decision == 'yes':
                    environment.send_contract_transaction(self._mediator_contract, buyer, 'finish', trade_id)
                    return
                elif confirmation_decision == 'no':
                    # buyer waits for confirmation, nothing happens
                    logger.debug('Seller contesting since no reaction from buyer')
                    environment.wait(int(self._timeout / 2))
                    environment.send_contract_transaction(self._mediator_contract, seller, 'contest', trade_id,
                                                          transfer_key)
                    environment.wait(self._timeout)
                    environment.send_contract_transaction(self._mediator_contract, seller, 'timeout', trade_id)
                    return
                else:
                    raise NotImplementedError()
            elif isinstance(errors[-1], encoding.LeafDigestMismatchError):
                if protocol_path.decide(buyer, 'Complain about Leaf', ['yes']) == 'yes':
                    error: encoding.NodeDigestMismatchError = errors[-1]
                    environment.send_contract_transaction(
                        self._verifier_contract, buyer,
                        'complainAboutLeaf',
                        trade_id,
                        error.index_out,
                        error.index_in,
                        error.out.data,
                        error.in1.data_as_list(),
                        error.in2.data_as_list(),
                        encrypted_merkle_tree.get_proof(error.out),
                        encrypted_merkle_tree.get_proof(error.in1)
                    )
                    return
            else:
                if protocol_path.decide(buyer, 'Complain about Node', ['yes']) == 'yes':
                    error = errors[-1]
                    environment.send_contract_transaction(
                        self._verifier_contract, buyer,
                        'complainAboutNode',
                        trade_id,
                        error.index_out,
                        error.index_in,
                        error.out.data,
                        error.in1.data_as_list(),
                        error.in2.data_as_list(),
                        encrypted_merkle_tree.get_proof(error.out),
                        encrypted_merkle_tree.get_proof(error.in1)
                    )
                    return


ProtocolManager.register('SmartJudge-FairSwap', SmartJudge)
