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
                 slices_count: int = 8, slice_length: int = 32, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._worst_case_cost = worst_cast_cost
        self._security_deposit = security_deposit
        self._timeout = timeout
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
        logger.debug('Initialization and sanitizing checks')

        logger.debug('Seller prepares the data')
        plain_data = data_provider.file_pointer.read()
        plain_merkle_tree = merkle.from_bytes(plain_data, self._slices_count)
        key = generate_bytes(32)

        # seller encrypts data and sends condition hash to buyer
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

        # seller creates condition hash
        # SmartJudge paper does explain precisely how condition_hashes get created/checked. In our opinion,
        # conditions_hash must be generated by seller because of containing the (plain) key. However, that can easily
        # be changed by using hash(key) instead of key. For additional remarks see README.md.
        conditions_hash = Web3.soliditySha3(
            ['bytes32', 'bytes32', 'bytes32'],
            [key, encrypted_merkle_tree.digest, plain_merkle_tree.digest]
        )
        agreement_hash = Web3.soliditySha3(['uint32', 'bytes32'], [self._verifier_id, conditions_hash])

        create_decision = protocol_path.decide(buyer, 'publish agreement', ['correct', 'incorrect'])
        if create_decision == 'correct':
            logger.debug('Buyer: create trade with correct agreement hash')
            transfer_agreement_hash = agreement_hash
        elif create_decision == 'incorrect':
            logger.debug('Buyer: create trade with incorrect agreement hash')
            transfer_agreement_hash = generate_bytes(len(agreement_hash), avoid=agreement_hash)
        else:
            raise NotImplementedError()

        environment.send_contract_transaction(self._mediator_contract, buyer, 'create', transfer_agreement_hash,
                                              value=self._security_deposit * environment.gas_price)
        trade_id = None
        for event in environment.event_filter(self._mediator_contract, 'TradeID', from_block=-1):
            trade_id = event['args']['_id']
            logger.debug('Trade has ID %i' % trade_id)
            break

        # === Mediator State: CREATED ===
        logger.debug('Seller: checking agreement_hash')
        if agreement_hash == transfer_agreement_hash:
            acceptance_decision = protocol_path.decide(seller, 'accept?', ['yes', 'no'])
            if acceptance_decision == 'yes':
                logger.debug('Seller: accept trade')
                environment.send_contract_transaction(self._mediator_contract, seller, 'accept', trade_id,
                                                      value=self._security_deposit * environment.gas_price)
            elif acceptance_decision == 'no':
                logger.debug('Seller: do not accept trade')
                environment.wait(self._timeout)
                logger.debug('Buyer: no reaction from seller, aborting')
                environment.send_contract_transaction(self._mediator_contract, buyer, 'abort', trade_id)
                return
            else:
                raise NotImplementedError()
        else:
            logger.debug('Seller: detected wrong agreement_hash, doing nothing')
            logger.debug('Buyer: seller does nothing, abort')
            environment.send_contract_transaction(self._mediator_contract, buyer, 'abort', trade_id)
            return

        # === Mediator State: ACCEPTED ===
        revelation_decision = protocol_path.decide(seller, 'reveal key?', ['correct', 'incorrect', 'skip'],
                                                   ['correct', 'skip'])
        if revelation_decision == 'correct':
            logger.debug('Seller: revealing correct key')
            transfer_key: Optional[bytes] = key
        elif revelation_decision == 'incorrect':
            logger.debug('Seller: revealing incorrect key')
            transfer_key = generate_bytes(len(key), avoid=key)
        elif revelation_decision == 'skip':
            logger.debug('Seller: Not revealing key (now)')
            transfer_key = None
        else:
            raise NotImplementedError()

        if transfer_key is not None:
            logger.debug('Buyer: trying to decrypt file')
            decrypted_merkle_tree, errors = encoding.decode(encrypted_merkle_tree, transfer_key)
            if decrypted_merkle_tree.digest == plain_merkle_tree.digest:
                logger.debug('Buyer: decryption successful')
                finish_decision = protocol_path.decide(buyer, 'finish?', ['yes', 'no'])
                if finish_decision == 'yes':
                    environment.send_contract_transaction(self._mediator_contract, buyer, 'finish', trade_id)
                    return
            else:
                logger.debug('Buyer: decryption not successful')

        contest_decision = protocol_path.decide(seller, 'contest/reveal', ['correct', 'incorrect'])
        if contest_decision == 'correct':
            logger.debug('Seller: contesting with correct key')
            contest_key = key
        elif contest_decision == 'incorrect':
            logger.debug('Seller: contesting with incorrect key')
            contest_key = generate_bytes(len(key), avoid=key)
        else:
            raise NotImplementedError()
        environment.send_contract_transaction(self._mediator_contract, seller, 'contest', trade_id, contest_key)

        # === Mediator State: CONTENDED ===
        decrypted_merkle_tree, errors = encoding.decode(encrypted_merkle_tree, contest_key)
        if decrypted_merkle_tree.digest == plain_merkle_tree.digest:
            finish_decision = protocol_path.decide(buyer, 'finish?', ['yes', 'no'])
            if finish_decision == 'yes':
                logger.debug('Buyer: confirming (correct) contest witness/finishing')
                environment.send_contract_transaction(self._mediator_contract, buyer, 'finish', trade_id)
                return
            elif finish_decision == 'no':
                logger.debug('Buyer: not confirming (correct) contest witness')
                logger.debug('Seller: wait for timeout')
                environment.wait(self._timeout)
                environment.send_contract_transaction(self._mediator_contract, seller, 'timeout', trade_id)
                return
            else:
                raise NotImplementedError()
        else:
            logger.debug('Buyer: retrieved unexpected file')
            environment.send_contract_transaction(self._mediator_contract, buyer, 'init_verification', trade_id,
                                                  self._verifier_id, conditions_hash)
            verify_initial_agreement_decision = protocol_path.decide(seller, 'verify initial agreement',
                                                                     ['correct', 'incorrect', 'leave'])
            if verify_initial_agreement_decision == 'correct':
                pass  # TODO implement
            elif verify_initial_agreement_decision == 'incorrect':
                pass  # TODO implement
            elif verify_initial_agreement_decision == 'leave':
                logger.debug('Seller: not verifying initial agreement')
                logger.debug('Buyer: requesting refund')
                environment.wait(self._timeout)
                environment.send_contract_transaction(self._verifier_contract, buyer, 'refund', trade_id)
                return
            else:
                raise NotImplementedError()


ProtocolManager.register('SmartJudge-FairSwap', SmartJudge)
