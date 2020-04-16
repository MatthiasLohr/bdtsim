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
import solcx  # type: ignore
from typing import Any, Dict, Optional, Tuple

SOLC_VERSION = 'v0.6.1'

logger = logging.getLogger(__name__)


class Contract(object):
    @property
    def abi(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @property
    def bytecode(self) -> str:
        raise NotImplementedError()


class SolidityContract(Contract):
    def __init__(self, contract_file: str, contract_name: str) -> None:
        self._contract_file = contract_file
        self._contract_name = contract_name
        self._abi: Optional[Dict[str, Any]] = None
        self._bytecode: Optional[str] = None

    @property
    def abi(self) -> Dict[str, Any]:
        if self._abi is None:
            self._abi, self._bytecode = self.compile(self._contract_file, self._contract_name)
        return self._abi

    @property
    def bytecode(self) -> str:
        if self._bytecode is None:
            self._abi, self._bytecode = self.compile(self._contract_file, self._contract_name)
        return self._bytecode

    @staticmethod
    def compile(contract_file: str, contract_name: str, solc_version: str = SOLC_VERSION) -> Tuple[Dict[str, Any], str]:
        # configure solc
        logger.debug('Checking for solc version %s' % solc_version)
        if solc_version not in solcx.get_installed_solc_versions():
            logger.debug('solc %s not found, installing...' % solc_version)
            solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version, silent=True)

        # read contract code
        with open(contract_file, 'r') as f:
            contract_code = f.read()

        compile_result = solcx.compile_source(contract_code)['<stdin>:' + contract_name]
        return compile_result.get('abi'), compile_result.get('bin')
