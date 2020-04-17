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

from eth_typing.evm import ChecksumAddress
from typing import Any, Optional
from web3 import Web3


class Participant(object):
    def __init__(self, name: str, wallet_address: Optional[str] = None, wallet_private_key: Optional[str] = None)\
            -> None:
        if wallet_address is None and wallet_private_key is None:
            raise ValueError('You have to provide at least wallet_address OR wallet_private_key')
        elif wallet_address is not None and wallet_private_key is not None:
            eth_account = Web3().eth.account.from_key(wallet_private_key)
            if eth_account.address != wallet_address:
                raise ValueError('wallet_private_key does not match wallet_address')
        elif wallet_address is None and wallet_private_key is not None:
            wallet_address = Web3().eth.account.from_key(wallet_private_key).address
        self._name = name
        self._wallet_address: ChecksumAddress = Web3.toChecksumAddress(wallet_address)
        self._wallet_private_key = wallet_private_key

    @property
    def name(self) -> str:
        return self._name

    @property
    def wallet_address(self) -> ChecksumAddress:
        return self._wallet_address

    @property
    def wallet_private_key(self) -> Optional[str]:
        return self._wallet_private_key

    def __str__(self) -> str:
        return '%s<%s>' % (self.name, self.wallet_address)

    def __repr__(self) -> str:
        return '<%s.%s name=%s wallet_address=%s has_wallet_private_key=%s>' % (
            __name__,
            self.__class__.__name__,
            self.name,
            self.wallet_address,
            str(self.wallet_private_key is not None)
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Participant)\
                and other.wallet_address == self.wallet_address\
                and other.name == self.name

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


operator = Participant(
    name='Operator',
    wallet_address='0x3ed8424aaE568b3f374e94a139D755982800a4a2',
    wallet_private_key='0xe67518b4d5255ec708d2bf9cd4222adda89fcc07037c614d7787a694fbb47692'
)

seller = Participant(
    name='Seller',
    wallet_address='0x5Afa5874959ff249103c2043fB45d68B2768Fef8',
    wallet_private_key='0x3df2d74ceb3c58a8fdb1f0ecf45e2ceb10511469d9c20691333d666fa557899a'
)

buyer = Participant(
    name='Buyer',
    wallet_address='0x00c382926f098566EA6F1707296eC342E7C8A5DC',
    wallet_private_key='0x7d96e8fbe712cf25f141adb6bc5e3244d7a19d9c406ab6ed6a097585d01b93ac'
)
