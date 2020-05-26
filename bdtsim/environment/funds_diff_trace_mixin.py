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

from typing import cast, Any

from web3 import Web3
from web3.datastructures import AttributeDict
from web3.types import RPCEndpoint


class FundsDiffTraceMixin(object):
    def __init__(self, web3: Web3) -> None:
        self._web3 = web3

    def _get_trace(self, tx_receipt: AttributeDict[str, Any]) -> AttributeDict[str, Any]:
        trace = self._web3.manager.request_blocking(RPCEndpoint('trace_transaction'),
                                                    [tx_receipt['transactionHash'].hex()])
        return cast(AttributeDict[str, Any], trace)
