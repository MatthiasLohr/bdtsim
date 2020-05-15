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

import json
from typing import Any

from bdtsim.account import Account
from bdtsim.protocol_path import Decision
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager
from .simulation_result import SimulationResult, TransactionLogEntry, TransactionLogList, TransactionLogCollection,\
    ResultNode


class JSONOutputFormat(OutputFormat):
    def __init__(self) -> None:
        super(JSONOutputFormat, self).__init__()

    def render(self, simulation_result: SimulationResult) -> None:
        print(json.dumps(simulation_result, cls=JSONEncoder))


class JSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Account):
            return {
                'name': obj.name,
                'wallet_address': obj.wallet_address
            }
        elif isinstance(obj, bytes):
            return '0x' + obj.hex()
        elif isinstance(obj, Decision):
            return {
                'account': obj.account,
                'description': obj.description,
                'variant': obj.outcome,
                'variants': obj.variants,
                'timestamp': obj.timestamp
            }
        elif isinstance(obj, ResultNode):
            return {
                'transactions': obj.tx_collection,
                'children': [{
                    'decision': decision,
                    'execution_results': child
                } for decision, child in obj.children.items()]
            }
        elif isinstance(obj, SimulationResult):
            return {
                'preparation_results': obj.preparation_transactions,
                'execution_results': obj.execution_result_root,
                'cleanup_results': obj.cleanup_transactions
            }
        elif isinstance(obj, TransactionLogCollection):
            return {
                'transaction_lists': obj.tx_log_lists,
                'aggregation': obj.aggregation
            }
        elif isinstance(obj, TransactionLogCollection.Aggregation):
            return list(obj.entries.values())
        elif isinstance(obj, TransactionLogEntry):
            return {
                'tx': obj.tx_dict,
                'receipt': obj.tx_receipt
            }
        elif isinstance(obj, TransactionLogCollection.Aggregation.Entry):
            return {
                'account': obj.account,
                'tx_fees_min': obj.tx_fees_min,
                'tx_fees_man': obj.tx_fees_max,
                'tx_fees_mean': obj.tx_fees_mean,
                'tx_count_min': obj.tx_count_min,
                'tx_count_man': obj.tx_count_max,
                'tx_count_mean': obj.tx_count_mean
            }
        elif isinstance(obj, TransactionLogList):
            return {
                'transactions': obj.tx_log_list,
                'aggregation': obj.aggregation
            }
        elif isinstance(obj, TransactionLogList.Aggregation):
            return list(obj.entries.values())
        elif isinstance(obj, TransactionLogList.Aggregation.Entry):
            return {
                'account': obj.account,
                'tx_fees': obj.tx_fees,
                'tx_count': obj.tx_count
            }
        else:
            return super(JSONEncoder, self).default(obj)


OutputFormatManager.register('json', JSONOutputFormat)
