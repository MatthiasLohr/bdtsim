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

from hexbytes import HexBytes
from json import JSONEncoder
from typing import List, Tuple, Any
from web3.datastructures import AttributeDict
from .participant import Participant
from .protocol_path import ProtocolPath


class SimulationResultCollector(object):
    _preparation_result = None
    _execution_results = []

    def set_preparation_result(self, result: Tuple):
        self._preparation_result = result

    def add_execution_result(self, protocol_path: ProtocolPath, logs: List[Tuple]):
        self._execution_results.append({
            'protocol_path': protocol_path,
            'transactions': [{
                'account': participant,
                'receipt': receipt
            } for participant, receipt in logs]
        })

    @property
    def preparation_result(self):
        return self._preparation_result

    @property
    def execution_results(self):
        return self._execution_results


class SimulationResultJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, AttributeDict):
            return dict(obj)
        elif isinstance(obj, HexBytes):
            return obj.hex()
        elif isinstance(obj, Participant):
            return {
                'name': obj.name,
                'wallet_address': obj.wallet_address,
                'wallet_private_key': obj.wallet_private_key
            }
        elif isinstance(obj, ProtocolPath):
            return obj.decisions_list
        elif isinstance(obj, SimulationResultCollector):
            result = {
                'preparation_result': {},
                'execution_results': obj.execution_results
            }
            if obj.preparation_result is not None:
                result['preparation_result'] = {
                    'account': obj.preparation_result[0],
                    'transaction': {
                        'receipt': obj.preparation_result[1]
                    }
                }
            return result
        return JSONEncoder.default(self, obj)
