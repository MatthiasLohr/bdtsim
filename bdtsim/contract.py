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
import os
from typing import Any, Dict, Optional, Tuple

import solcx  # type: ignore


SOLC_DEFAULT_VERSION = 'v0.6.1'

logger = logging.getLogger(__name__)


class Contract(object):
    def __init__(self, abi: Dict[str, Any], bytecode: str, address: Optional[str] = None) -> None:
        self._abi = abi
        self._bytecode = bytecode
        self._address = address

    @property
    def abi(self) -> Dict[str, Any]:
        return self._abi

    @property
    def bytecode(self) -> str:
        return self._bytecode

    @property
    def address(self) -> Optional[str]:
        return self._address

    @address.setter
    def address(self, address: str) -> None:
        self._address = address


class SolidityContract(Contract):
    def __init__(self, contract_name: str, contract_file: Optional[str] = None, contract_code: Optional[str] = None,
                 solc_version: str = SOLC_DEFAULT_VERSION, compiler_kwargs: Optional[Dict[str, Any]] = None) -> None:

        if compiler_kwargs is None:
            compiler_kwargs = {}

        if contract_file is not None and contract_code is not None:
            raise ValueError('contract_file and contract_code cannot be set at the same time')

        if contract_file is not None:
            logger.debug('Preparing to compile contract "%s" from file %s' % (contract_name, contract_file))
            with open(contract_file, 'r') as f:
                contract_code = f.read()
        else:
            logger.debug('Preparing to compile contract "%s" with given code' % contract_name)

        if contract_code is None or len(contract_code) == 0:
            raise ValueError('No contract code given')

        abi, bytecode = self.compile(contract_name, contract_code, compiler_kwargs, solc_version)
        super(SolidityContract, self).__init__(abi, bytecode)

    @staticmethod
    def compile(contract_name: str, contract_code: str, compiler_kwargs: Optional[Dict[str, Any]] = None,
                solc_version: str = SOLC_DEFAULT_VERSION) -> Tuple[Dict[str, Any], str]:
        # configure solc
        logger.debug('Checking for solc version %s' % solc_version)
        if solc_version not in solcx.get_installed_solc_versions():
            logger.debug('solc %s not found, installing...' % solc_version)
            solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version, silent=True)
        compile_result = solcx.compile_source(
            source=contract_code,
            **compiler_kwargs
        )['<stdin>:' + contract_name]
        return compile_result.get('abi'), compile_result.get('bin')
