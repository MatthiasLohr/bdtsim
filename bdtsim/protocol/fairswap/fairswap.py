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
from typing import Any, Optional

from eth_utils.crypto import keccak
from jinja2 import Template

from bdtsim.protocol import Protocol, ProtocolManager
from bdtsim.contract import SolidityContract
from bdtsim.environment import Environment
from bdtsim.participant import Participant, buyer
from bdtsim.protocol_path import ProtocolPath


class FairSwap(Protocol):
    def __init__(self, contract_template_file: str, *args: Any, depth: Optional[int] = 16, length: Optional[int] = 16,
                 n: Optional[int] = 16, receiver: Optional[Participant] = None, price: Optional[int] = 1000000000,
                 key_commit: Optional[str] = None, ciphertext_root: Optional[str] = None,
                 file_root: Optional[str] = None, **kwargs: Any) -> None:

        super(FairSwap, self).__init__(*args, **kwargs)
        self._contract_template_file = contract_template_file

        self._depth = depth
        self._length = length
        self._n = n
        if receiver is None:
            self._receiver = buyer.wallet_address
        else:
            self._receiver = receiver.wallet_address
        self._price = price
        self._key_commit = key_commit or '0x' + keccak(b'key').hex()
        self._ciphertext_root = ciphertext_root or '0x' + keccak(b'cipher').hex()
        self._file_root = file_root or '0x' + keccak(b'plain').hex()

    @property
    def contract(self) -> Optional[SolidityContract]:
        contract_template_path = self.contract_path(__file__, self._contract_template_file)
        with open(contract_template_path, 'r') as f:
            contract_code = f.read()
        contract_template = Template(contract_code)
        contract_rendered = contract_template.render(
            depth=self._depth,
            length=self._length,
            n=self._n,
            receiver=self._receiver,
            price=self._price,
            key_commit=self._key_commit,
            ciphertext_root=self._ciphertext_root,
            file_root=self._file_root
        )
        return SolidityContract('FileSale', contract_code=contract_rendered)

    @property
    def contract_is_reusable(self) -> bool:
        return False

    def run(self, protocol_path: ProtocolPath, environment: Environment, seller: Participant,
            buyer: Participant) -> None:
        pass


ProtocolManager.register('FairSwap-FileSale', FairSwap, 'FairFileSale.tpl.sol')
