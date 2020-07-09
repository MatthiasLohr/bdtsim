import logging
from jinja2 import Template
from web3 import Web3
from ecdsa import SigningKey, SECP256k1  # type: ignore   seems to be not  PEP 561 compliant
from typing import Any, Optional
import random

from bdtsim.account import Account
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.protocol_path import ProtocolPath

logger = logging.getLogger(__name__)


class Delgado(Protocol):
    CONTRACT_TEMPLATE_FILE = 'delgado-trade/delgadoTrade.tpl.sol'
    CONTRACT_NAME = 'Delgado'

    def __init__(self,  timeout: int = 600, *args: Any, **kwargs: Any) -> None:
        super(Delgado, self).__init__(*args, **kwargs)
        self._timeout = int(timeout)

    def _get_contract(self, price: int) -> SolidityContract:
        """
        Args:
            buyer (Account): Account which has to pay and will receive the data
            price (int): Price of the data to be traded in Wei
            pubkey
            key_hash (bytes): bytes32 keccak hash of key to be used

        Returns:
            SolidityContract: Actual smart contract to be deployed with pre-filled values
        """
        with open(self.contract_path(__file__, Delgado.CONTRACT_TEMPLATE_FILE)) as f:
            contract_template = Template(f.read())
        contract_code_rendered = contract_template.render(
            time=self._timeout,
            # receiver=buyer.wallet_address,
            price=price,
        )

        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code_rendered)

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

        # plain_data = data_provider.file_pointer.read()
        # === 1: Seller: encrypt file for transmission
        # encryption_decision = protocol_path.decide(
        #    seller, 'File Encryption/Transfer', ['expected','unexpected key','unexpected file']
        # )
        # TODO data exchange beforehand - simulate or not?
        sk = SigningKey.generate(curve=SECP256k1)  # private key
        # exchange with buyer
        vk = sk.verifying_key      # public key
        pubkX = vk.pubkey.point.x()
        pubkY = vk.pubkey.point.y()
        # === 2a: Seller send encrypted
        # TODO
        # === 2b: Buyer challenges Seller
        # TODO
        # === 2c: Seller answers challenges and sends SIG
        # TODO
        # === 3: Buyer: deploy smart contract
        construct_contract_decision = protocol_path.decide(seller, 'InitializeContract', ['dummy'])
        logging.debug(construct_contract_decision.description)
        # actual contract deployment
        environment.deploy_contract(buyer, self._get_contract(
            price=price,
        ))
        init_contract_decision = protocol_path.decide(seller, 'BuyerInitTrade', ['dummy'])
        logging.debug(init_contract_decision.description)
        # === 4: Buyer: init contract
        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkX, pubkY, seller.wallet_address)
        environment.send_contract_transaction(
            buyer, 'BuyerInitTrade', pubkX, pubkY, Web3.toChecksumAddress(seller.wallet_address), value=price)

        # === 5: Seller: Reveal key ===
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', ['yes', 'leave'])
        if key_revelation_decision == 'yes':
            pN = int(sk.to_string().hex(), 16)
            environment.send_contract_transaction(seller, 'SellerRevealKey', pN)
        elif key_revelation_decision == 'leave':
            logger.debug('Seller: Leaving without Key Revelation')
            if protocol_path.decide(buyer, 'Refund', variants=['yes', 'no']) == 'yes':
                logger.debug('Buyer: Waiting for timeout to request refund')
                environment.wait(self._timeout + 1)
                environment.send_contract_transaction(buyer, 'refund')
            return
        else:
            raise NotImplementedError()

        # === 6: Buyer: Check key ===
        # TODO

    @staticmethod
    def generate_bytes(length: int = 32, seed: Optional[int] = None, avoid: Optional[bytes] = None) -> bytes:
        if seed is not None:
            random.seed(seed)
        tmp = avoid
        while tmp is None or tmp == avoid:
            tmp = bytes(bytearray(random.getrandbits(8) for _ in range(length)))
        return tmp


ProtocolManager.register('Delgado-FileSale', Delgado)
