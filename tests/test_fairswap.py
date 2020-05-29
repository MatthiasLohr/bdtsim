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

import math
import unittest

from eth_tester import EthereumTester, PyEVMBackend
from eth_utils.crypto import keccak
from web3 import Web3, EthereumTesterProvider

from bdtsim.account import buyer
from bdtsim.protocol.fairswap import FairSwap
from bdtsim.protocol.fairswap.encoding import encode, decode, B032, crypt
from bdtsim.protocol.fairswap.merkle import MerkleTreeNode, MerkleTreeLeaf, from_bytes


class FairSwapTest(unittest.TestCase):
    def test_keccak(self):
        data = FairSwap.generate_bytes(32)
        self.assertEqual(keccak(data), Web3.solidityKeccak(['bytes32'], [data]))
        self.assertEqual(keccak(data), Web3.solidityKeccak(['bytes32[1]'], [[data]]))
        self.assertEqual(keccak(data), Web3.keccak(data))


class MerkleTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, MerkleTreeNode, MerkleTreeLeaf(B032), MerkleTreeLeaf(B032), MerkleTreeLeaf(B032))

    def test_get_proof_and_validate(self):
        for slice_count in [2, 4, 8, 16]:
            tree = from_bytes(FairSwap.generate_bytes(32 * slice_count), slice_count)
            for index, leaf in enumerate(tree.leaves):
                proof = tree.get_proof(leaf)
                self.assertEqual(len(proof), int(math.log2(slice_count)))
                self.assertTrue(MerkleTreeNode.validate_proof(tree.digest, leaf, index, proof))


class EncodingTest(unittest.TestCase):
    def test_encode_decode(self):
        tree = from_bytes(FairSwap.generate_bytes(128, seed=42), 4)
        tree_enc = encode(tree, B032)
        tree_dec, errors = decode(tree_enc, B032)
        self.assertEqual([], errors)
        self.assertEqual(tree, tree_dec)


class ContractTest(unittest.TestCase):
    @staticmethod
    def prepare_contract(file_root_hash, ciphertext_root_hash, key_hash, slice_count: int = 4):
        web3 = Web3(EthereumTesterProvider(EthereumTester(PyEVMBackend())))
        contract_object = FairSwap(slice_count)._get_contract(
            buyer=buyer,
            price=1000000000,
            slice_length=32,
            file_root_hash=file_root_hash,
            ciphertext_root_hash=ciphertext_root_hash,
            key_hash=key_hash
        )
        contract_preparation = web3.eth.contract(abi=contract_object.abi, bytecode=contract_object.bytecode)
        tx_hash = contract_preparation.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        return web3, web3.eth.contract(address=tx_receipt.contractAddress, abi=contract_object.abi)

    def test_vrfy(self):
        tree = from_bytes(FairSwap.generate_bytes(128, seed=42), 4)
        key = FairSwap.generate_bytes(32, seed=43)
        tree_enc = encode(tree, key)
        web3, contract = self.prepare_contract(tree.digest, tree_enc.digest, B032)

        for index, leaf in enumerate(tree_enc.leaves):
            proof = tree_enc.get_proof(leaf)
            self.assertEqual(len(proof), 3)
            call_result = contract.functions.vrfy(index, leaf.digest, proof).call()
            self.assertTrue(call_result)

    def test_crypt_small(self):
        for n in [4, 8, 16]:
            web3, contract = self.prepare_contract(FairSwap.generate_bytes(32), FairSwap.generate_bytes(32), B032, n)
            for i in range(8):
                data = FairSwap.generate_bytes(32)
                call_result = contract.functions.cryptSmall(i, data).call()
                self.assertEqual(call_result, crypt(data, n + i, B032))
