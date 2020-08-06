import logging
from jinja2 import Template
from web3 import Web3
from ecdsa import SigningKey, SECP256k1  # type: ignore
# seems to be not  PEP 561 compliant
from typing import Any, Optional, cast
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
    REUSABLE_CONTRACT_FILE = 'delgado-trade/delgadoVariable.sol'
    CONTRACT_NAME = 'Delgado'

    def __init__(self,  timeout: int = 600, *args: Any, **kwargs: Any) -> None:
        super(Delgado, self).__init__(*args, **kwargs)
        self._timeout = int(timeout)
        self._sk = SigningKey.generate(curve=SECP256k1)
        _vk = self._sk.verifying_key
        self._pubkX = _vk.pubkey.point.x()
        self._pubkY = _vk.pubkey.point.y()

    def _get_contract(self, price: int) -> SolidityContract:
        """
        Args:
            price (int): Price of the data to be traded in Wei

        Returns:
            SolidityContract: Actual smart contract to be deployed with pre-filled values
        """
        with open(self.contract_path(__file__, Delgado.CONTRACT_TEMPLATE_FILE)) as f:
            contract_template = Template(f.read())
        contract_code_rendered = contract_template.render(
            time=self._timeout,
            price=price,
        )

        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code_rendered)

    def execute(self, protocol_path: ProtocolPath, environment: Environment, data_provider: DataProvider,
                seller: Account, buyer: Account, price: int = 1000000000) -> None:
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
        # TODO data exchange beforehand - simulate or not?

        # === 2a: Seller send encrypted
        # TODO
        # === 2b: Buyer challenges Seller
        # TODO
        # === 2c: Seller answers challenges and sends SIG
        # TODO
        # === 3: Buyer: extract pubX and pubY from SIG-> deploy smart contract
        # Currently done in init due to no actual transmission

        # contract deployment and initializasion
        self.smart_contract_init(environment, seller, buyer, self._timeout, self._pubkX, self._pubkY, price)
        # === 5: Seller: Reveal key ===
        key_revelation_decision = protocol_path.decide(seller, 'Key Revelation', ['yes', 'no'])
        if key_revelation_decision == 'yes':
            pN = int(self._sk.to_string().hex(), 16)
            self.smart_contract_reveal_key(environment, seller, buyer, pN, self._pubkY)
        elif key_revelation_decision == 'no':
            logger.debug('Seller: Leaving without Key Revelation')
            if protocol_path.decide(buyer, 'Refund', variants=['yes', 'no']) == 'yes':
                logger.debug('Buyer: Waiting for timeout to request refund')
                environment.wait(self._timeout + 1)
                self.smart_contract_refund(environment, seller, buyer, self._pubkY, buyer)
                return

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

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, timeout: int,
                            pubkX: int, pubkY: int, price: int) -> None:
        environment.deploy_contract(buyer, self._get_contract(
            price=price,
        ))
        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkX, pubkY, seller.wallet_address)
        environment.send_contract_transaction(
            buyer, 'BuyerInitTrade', pubkX, pubkY, Web3.toChecksumAddress(seller.wallet_address), value=price)

    @staticmethod
    def smart_contract_reveal_key(environment: Environment, seller: Account, buyer: Account,
                                  pN: int, pubY: int) -> None:
        environment.send_contract_transaction(seller, 'SellerRevealKey', pN)

    @staticmethod
    def smart_contract_refund(environment: Environment, seller: Account, buyer: Account, pubY: int,
                              beneficiary: Account) -> None:
        environment.send_contract_transaction(beneficiary, 'refund')


class DelgadoReusable(Delgado):
    def _get_reusable_contract(self) -> SolidityContract:
        with open(self.contract_path(__file__, Delgado.REUSABLE_CONTRACT_FILE)) as f:
            contract_code = f.read()
        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code)

    @staticmethod
    def get_session_id(seller: Account, buyer: Account, pubY: int) -> bytes:
        return cast(bytes, Web3.solidityKeccak(
            ['address', 'address', 'uint256'],
            [seller.wallet_address, buyer.wallet_address, pubY]
        ))

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        logger.debug('Deploying reusable smart contract...')
        environment.deploy_contract(operator, self._get_reusable_contract())

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, timeout: int,
                            pubkX: int, pubkY: int, price: int) -> None:
        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkX, pubkY, seller.wallet_address)
        environment.send_contract_transaction(
            buyer, 'BuyerInitTrade', pubkX, pubkY, timeout, seller.wallet_address, value=price)

    @staticmethod
    def smart_contract_reveal_key(environment: Environment, seller: Account, buyer: Account,
                                  pN: int, pubY: int) -> None:
        session_id = DelgadoReusable.get_session_id(seller, buyer, pubY)
        environment.send_contract_transaction(seller, 'SellerRevealKey', session_id, pN)

    @staticmethod
    def smart_contract_refund(environment: Environment, seller: Account, buyer: Account, pubY: int,
                              beneficiary: Account) -> None:
        session_id = DelgadoReusable.get_session_id(seller, buyer, pubY)
        environment.send_contract_transaction(beneficiary, 'refund', session_id)


ProtocolManager.register('Delgado', Delgado)
ProtocolManager.register('Delgado-Reusable', DelgadoReusable)
