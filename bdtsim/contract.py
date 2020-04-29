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
from typing import Any, Dict, Optional, Tuple

import solcx  # type: ignore


SOLC_VERSION = 'v0.6.1'

logger = logging.getLogger(__name__)


class SolidityContract(object):
    def __init__(self, contract_name: str, contract_file: Optional[str] = None,
                 contract_code: Optional[str] = None) -> None:

        if contract_file is not None and contract_code is not None:
            raise ValueError('contract_file and contract_code cannot be set at the same time')

        self._contract_name = contract_name
        if contract_file is not None:
            with open(contract_file, 'r') as f:
                self._contract_code = f.read()
        elif contract_code is not None:
            self._contract_code = contract_code
        else:
            raise ValueError('contract_file and contract_code cannot be None at the same time')

        self._abi: Optional[Dict[str, Any]] = None
        self._bytecode: Optional[str] = None

    @property
    def abi(self) -> Dict[str, Any]:
        if self._abi is None:
            self._abi, self._bytecode = self.compile(self._contract_name, self._contract_code)
        return self._abi

    @property
    def bytecode(self) -> str:
        if self._bytecode is None:
            self._abi, self._bytecode = self.compile(self._contract_name, self._contract_code)
        return self._bytecode

    @staticmethod
    def compile(contract_name: str, contract_code: str, solc_version: str = SOLC_VERSION) -> Tuple[Dict[str, Any], str]:
        # configure solc
        logger.debug('Checking for solc version %s' % solc_version)
        if solc_version not in solcx.get_installed_solc_versions():
            logger.debug('solc %s not found, installing...' % solc_version)
            solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version, silent=True)
        compile_result = solcx.compile_source(contract_code)['<stdin>:' + contract_name]
        return compile_result.get('abi'), compile_result.get('bin')
