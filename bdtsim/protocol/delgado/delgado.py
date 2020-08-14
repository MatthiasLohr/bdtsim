import logging
from jinja2 import Template
from web3 import Web3
from ecdsa import SigningKey, SECP256k1  # type: ignore
# seems to be not  PEP 561 compliant
from typing import Any, cast

from bdtsim.account import Account
from bdtsim.contract import SolidityContract
from bdtsim.data_provider import DataProvider
from bdtsim.environment import Environment
from bdtsim.protocol import Protocol, ProtocolManager, DEFAULT_ASSET_PRICE
from bdtsim.protocol_path import ProtocolPath

logger = logging.getLogger(__name__)


class Delgado(Protocol):
    REUSABLE_LIBRARY_FILE = 'delgado-trade/EllipticCurve.sol'
    CONTRACT_TEMPLATE_FILE = 'delgado-trade/delgadoTrade.tpl.sol'
    CONTRACT_LIBRARY_TEMPLATE_FILE = 'delgado-trade/delgadoTradeLibrary.tpl.sol'
    REUSABLE_CONTRACT_FILE = 'delgado-trade/delgadoVariable.tpl.sol'
    CONTRACT_NAME = 'Delgado'
    LIBRARY_NAME = 'EllipticCurve'

    def __init__(self,  timeout: int = 600, *args: Any, **kwargs: Any) -> None:
        super(Delgado, self).__init__(*args, **kwargs)
        self._timeout = int(timeout)

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
            lib=Web3.toChecksumAddress(self._library_address),

        )

        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code_rendered)

    def _get_library_contract(self) -> SolidityContract:
        with open(self.contract_path(__file__, Delgado.REUSABLE_LIBRARY_FILE)) as f:
            contract_code = f.read()
        return SolidityContract(Delgado.LIBRARY_NAME, contract_code=contract_code)

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
        # === 1 Buyer get encrypted data
        # TODO
        # === 2a: Seller send encrypted file and public key with whom he encrypted the data
        # TODO

        # === 2b: Buyer challenges Seller multiple times 
        # TODO
        # === 2c: Seller answers challenges(with proofs) (repeat 2b until sure)
        # TODO

        # === 3a: Buyer request ECDSA signature of seller with a certain nonce 
        # TODO

        # === 3b: Seller sends signature
        # TODO

        # === 4a: Buyer verifies ECDSA signature of seller with public key
        # TODO

        # === 4b Buyer: extract pubX and pubY from SIG-> deploy smart contract
        self._sk = SigningKey.generate(curve=SECP256k1)
        _vk = self._sk.verifying_key
        self._pubkX = _vk.pubkey.point.x()
        self._pubkY = _vk.pubkey.point.y()

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

        # === 6: Buyer: Decode data===
        # TODO

    def prepare_iteration(self, environment: Environment, operator: Account) -> None:
        logger.debug('Deploying reusable library contract...')
        self._library_address = Web3.toChecksumAddress(
                                environment.deploy_library(operator, self._get_library_contract()))

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, timeout: int,
                            pubkX: int, pubkY: int, price: int) -> None:
        environment.deploy_contract(buyer, self._get_contract(
            price=price,
            )
        )
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
            contract_template = Template(f.read())
            contract_code_rendered = contract_template.render(
                lib=self._library_address,
            )
        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code_rendered)

    @staticmethod
    def get_session_id(seller: Account, buyer: Account, pubY: int) -> bytes:
        return cast(bytes, Web3.solidityKeccak(
            ['address', 'address', 'uint256'],
            [seller.wallet_address, buyer.wallet_address, pubY]
        ))

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        logger.debug('Deploying reusable smart contract...')
        logger.debug('Deploying reusable library contract...')
        self._library_address = Web3.toChecksumAddress(
                                environment.deploy_library(operator, self._get_library_contract()))
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


class DelgadoLibrary(Delgado):
    def _get_delgado_library_contract(self, price: int) -> SolidityContract:
        with open(self.contract_path(__file__, Delgado.CONTRACT_LIBRARY_TEMPLATE_FILE)) as f:
            contract_template = Template(f.read())
            contract_code_rendered = contract_template.render(
                time=self._timeout,
                price=price,
                lib=self._library_address,
            )
        return SolidityContract(Delgado.CONTRACT_NAME, contract_code=contract_code_rendered)

    def smart_contract_init(self, environment: Environment, seller: Account, buyer: Account, timeout: int,
                            pubkX: int, pubkY: int, price: int) -> None:
        environment.deploy_contract(buyer, self._get_delgado_library_contract(
            price=price,
        ))
        logger.debug("pubX: %d, pubY: %d, seller: %s", pubkX, pubkY, seller.wallet_address)
        environment.send_contract_transaction(
            buyer, 'BuyerInitTrade', pubkX, pubkY, seller.wallet_address, value=price)

    def prepare_simulation(self, environment: Environment, operator: Account) -> None:
        logger.debug('Deploying reusable library contract...')
        self._library_address = Web3.toChecksumAddress(
                                environment.deploy_library(operator, self._get_library_contract()))


ProtocolManager.register('Delgado', Delgado)
ProtocolManager.register('Delgado-Library', DelgadoLibrary)
ProtocolManager.register('Delgado-Reusable', DelgadoReusable)
