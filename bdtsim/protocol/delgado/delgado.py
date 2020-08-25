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
from typing import Any, Optional, cast

from ecdsa.curves import SECP256k1  # type: ignore
from ecdsa.keys import SigningKey  # type: ignore
from web3 import Web3

from bdtsim.account import Account
from bdtsim.contract import SolidityContract, SolidityContractCollection
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, DEFAULT_ASSET_PRICE
from bdtsim.protocol_path import ProtocolPath


logger = logging.getLogger(__name__)


class DelgadoBasic(Protocol):
    CONTRACT_NAME = 'Delgado'
    CONTRACT_TEMPLATE_FILENAME = 'DelgadoBasic.tpl.sol'
    LIBRARY_NAME = 'EllipticCurve'
    LIBRARY_FILENAME = 'EllipticCurve.sol'

    def __init__(self,  timeout: int = 600, *args: Any, **kwargs: Any) -> None:
        super(DelgadoBasic, self).__init__(*args, **kwargs)
        self.timeout = int(timeout)

        self._contract_collection = SolidityContractCollection('0.6.1')
        self._contract_collection.add_contract_file(
            self.LIBRARY_NAME,
            self.contract_path(__file__, self.LIBRARY_FILENAME)
        )
        self.library = self._contract_collection.get(self.LIBRARY_NAME)
        self.contract: Optional[SolidityContract] = None

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = DEFAULT_ASSET_PRICE) -> None:
        """Execute a file transfer using the Delgado protocol.

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
        # Steps 1-4a are not covered by the simulation due to the lack of blockchain interaction
        # These steps are assumed to be already done
        # === 1 Buyer get encrypted data
        # === 2a: Seller send encrypted file and public key with whom he encrypted the data
        # === 2b: Buyer challenges Seller multiple times
        # === 2c: Seller answers challenges(with proofs) (repeat 2b until sure)
        # === 3a: Buyer request ECDSA signature of seller with a certain nonce
        # === 3b: Seller sends signature
        # === 4a: Buyer verifies ECDSA signature of seller with public key

        # === 4b Buyer: extract pubX and pubY from SIG-> deploy smart contract
        signing_key = SigningKey.generate(curve=SECP256k1)
        verifying_key = signing_key.verifying_key
        pubkey_x = verifying_key.pubkey.point.x()
        pubkey_y = verifying_key.pubkey.point.y()

        # contract deployment and initialization
        self.smart_contract_init(environment, seller, buyer, pubkey_x, pubkey_y, price)

        # === 5: Seller: Reveal key ===
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', ['yes', 'no'])
        if key_revelation_decision == 'yes':
            private_number = int(signing_key.to_string().hex(), 16)
            self.smart_contract_reveal_key(environment, seller, buyer, private_number, pubkey_y)
        elif key_revelation_decision == 'no':
            logger.debug('Seller: Leaving without Key Revelation')
            if protocol_path.decide(buyer, 'Refund', variants=['yes', 'no']) == 'yes':
                logger.debug('Buyer: Waiting for timeout to request refund')
                environment.wait(self.timeout + 1)
                self.smart_contract_refund(environment, seller, buyer, pubkey_y, buyer)
                return

        # === 6: Buyer: Decode data===
        # off-chain task, therefore not implemented here

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, pubkey_x: int,
                            pubkey_y: int, price: int) -> None:
        environment.deploy_contract(buyer, self.library)

        self._contract_collection.add_contract_template_file(
            self.CONTRACT_NAME,
            self.contract_path(__file__, self.CONTRACT_TEMPLATE_FILENAME),
            {
                'time': self.timeout,
                'price': price,
                'lib': self.library.address
            }
        )
        self.contract = self._contract_collection.get(self.CONTRACT_NAME)
        environment.deploy_contract(buyer, self.contract)

        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkey_x, pubkey_y, seller.wallet_address)
        environment.send_contract_transaction(self.contract, buyer, 'BuyerInitTrade', pubkey_x, pubkey_y,
                                              Web3.toChecksumAddress(seller.wallet_address), value=price)

    def smart_contract_reveal_key(self, environment: Environment, seller: Account, buyer: Account,
                                  private_number: int, pubkey_y: int) -> None:
        if self.contract is None:
            raise RuntimeError('Contract not initialized!')
        environment.send_contract_transaction(self.contract, seller, 'SellerRevealKey', private_number)

    def smart_contract_refund(self, environment: Environment, seller: Account, buyer: Account, pubkey_y: int,
                              beneficiary: Account) -> None:
        if self.contract is None:
            raise RuntimeError('Contract not initialized!')
        environment.send_contract_transaction(self.contract, beneficiary, 'refund')


class DelgadoReusableLibrary(DelgadoBasic):
    CONTRACT_TEMPLATE_FILENAME = 'DelgadoReusableLibrary.tpl.sol'

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        environment.deploy_contract(operator, self.library)

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, pubkey_x: int,
                            pubkey_y: int, price: int) -> None:

        self._contract_collection.add_contract_template_file(
            self.CONTRACT_NAME,
            self.contract_path(__file__, self.CONTRACT_TEMPLATE_FILENAME),
            {
                'time': self.timeout,
                'price': price,
                'lib': self.library.address
            }
        )
        self.contract = self._contract_collection.get(self.CONTRACT_NAME)
        environment.deploy_contract(buyer, self.contract)

        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkey_x, pubkey_y, seller.wallet_address)
        environment.send_contract_transaction(self.contract, buyer, 'BuyerInitTrade', pubkey_x, pubkey_y,
                                              seller.wallet_address, value=price)


class DelgadoReusableContract(DelgadoBasic):
    CONTRACT_TEMPLATE_FILENAME = 'DelgadoReusableContract.tpl.sol'

    @staticmethod
    def get_session_id(seller: Account, buyer: Account, pubkey_x: int) -> bytes:
        return cast(bytes, Web3.solidityKeccak(
            ['address', 'address', 'uint256'],
            [seller.wallet_address, buyer.wallet_address, pubkey_x]
        ))

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        environment.deploy_contract(operator, self.library)

        self._contract_collection.add_contract_template_file(
            self.CONTRACT_NAME,
            self.contract_path(__file__, self.CONTRACT_TEMPLATE_FILENAME),
            {
                'time': self.timeout,
                'lib': self.library.address
            }
        )
        self.contract = self._contract_collection.get(self.CONTRACT_NAME)
        environment.deploy_contract(operator, self.contract)

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, pubkey_x: int,
                            pubkey_y: int, price: int) -> None:
        if self.contract is None:
            raise RuntimeError('Contract not initialized!')
        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkey_x, pubkey_y, seller.wallet_address)
        environment.send_contract_transaction(self.contract, buyer, 'BuyerInitTrade', pubkey_x, pubkey_y, self.timeout,
                                              seller.wallet_address, value=price)

    def smart_contract_reveal_key(self, environment: Environment, seller: Account, buyer: Account, private_number: int,
                                  pubkey_y: int) -> None:
        if self.contract is None:
            raise RuntimeError('Contract not initialized!')
        session_id = self.get_session_id(seller, buyer, pubkey_y)
        environment.send_contract_transaction(self.contract, seller, 'SellerRevealKey', session_id, private_number)

    def smart_contract_refund(self, environment: Environment, seller: Account, buyer: Account, pubkey_y: int,
                              beneficiary: Account) -> None:
        if self.contract is None:
            raise RuntimeError('Contract not initialized!')
        session_id = self.get_session_id(seller, buyer, pubkey_y)
        environment.send_contract_transaction(self.contract, beneficiary, 'refund', session_id)


ProtocolManager.register('Delgado', DelgadoBasic)
ProtocolManager.register('Delgado-ReusableLibrary', DelgadoReusableLibrary)
ProtocolManager.register('Delgado-ReusableContract', DelgadoReusableContract)
