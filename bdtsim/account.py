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

import os
import pathlib
import platform
from typing import Any, Optional, Union

import yaml
from eth_typing.evm import ChecksumAddress
from hexbytes.main import HexBytes
from web3.auto import w3 as web3


class Account(object):
    def __init__(self, name: str, wallet_private_key: Union[bytes, str]) -> None:
        if wallet_private_key is None:
            raise ValueError('You have to provide the private key for the wallet!')
        if isinstance(wallet_private_key, str):
            if wallet_private_key.startswith('0x'):
                self._wallet_private_key = HexBytes.fromhex(wallet_private_key[2:])
            else:
                self._wallet_private_key = HexBytes.fromhex(wallet_private_key)
        elif isinstance(wallet_private_key, bytes):
            self._wallet_private_key = wallet_private_key
        else:
            raise ValueError('Type not supported')

        self._name = name
        self._wallet_address: ChecksumAddress = web3.eth.account.from_key(wallet_private_key).address

    @property
    def name(self) -> str:
        return self._name

    @property
    def wallet_address(self) -> ChecksumAddress:
        return self._wallet_address

    @property
    def wallet_private_key(self) -> bytes:
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
        if isinstance(other, Account):
            return self.wallet_address == other.wallet_address and self.name == other.name
        else:
            raise NotImplementedError()

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.wallet_address, self.name))


class AccountFile(object):
    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = self.get_default_path()

        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = yaml.load(f, Loader=yaml.SafeLoader)
            self._operator = Account(
                name=data['accounts']['operator']['name'],
                wallet_private_key=data['accounts']['operator']['privateKey']
            )
            self._seller = Account(
                name=data['accounts']['seller']['name'],
                wallet_private_key=data['accounts']['seller']['privateKey']
            )
            self._buyer = Account(
                name=data['accounts']['buyer']['name'],
                wallet_private_key=data['accounts']['buyer']['privateKey']
            )
        else:
            self._operator = Account(name='Operator', wallet_private_key=web3.eth.account.create().privateKey)
            self._seller = Account(name='Seller', wallet_private_key=web3.eth.account.create().privateKey)
            self._buyer = Account(name='Buyer', wallet_private_key=web3.eth.account.create().privateKey)
            self._path = self.get_default_path()
            self.write()

    @property
    def operator(self) -> Account:
        return self._operator

    @operator.setter
    def operator(self, operator: Account) -> None:
        self._operator = operator

    @property
    def seller(self) -> Account:
        return self._seller

    @seller.setter
    def seller(self, seller: Account) -> None:
        self._seller = seller

    @property
    def buyer(self) -> Account:
        return self._buyer

    @buyer.setter
    def buyer(self, buyer: Account) -> None:
        self._buyer = buyer

    @staticmethod
    def get_default_path() -> str:
        system = platform.system()
        if system in ('Linux', 'Darwin'):
            return os.path.join(str(pathlib.Path.home()), '.config', 'bdtsim', 'accounts.yaml')
        elif system == 'Windows':
            app_data_dir = os.getenv('APPDATA')
            if app_data_dir is not None:
                return os.path.join(app_data_dir, 'bdtsim', 'accounts.yaml')
            else:
                return os.path.join(str(pathlib.Path.home()), 'bdtsim', 'accounts.yaml')
        else:
            return os.path.join(str(pathlib.Path.home()), 'bdtsim', 'accounts.yaml')

    def write(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, 'w') as f:
            yaml.dump({
                'accounts': {
                    'operator': {
                        'name': self._operator.name,
                        'privateKey': self._operator.wallet_private_key.hex()
                    },
                    'seller': {
                        'name': self._seller.name,
                        'privateKey': self._seller.wallet_private_key.hex()
                    },
                    'buyer': {
                        'name': self._buyer.name,
                        'privateKey': self._buyer.wallet_private_key.hex()
                    }
                }
            }, f)
