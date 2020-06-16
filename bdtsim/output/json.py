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
    def default(self, o: Any) -> Any:
        if isinstance(o, Account):
            return {
                'name': o.name,
                'wallet_address': o.wallet_address
            }
        elif isinstance(o, bytes):
            return '0x' + o.hex()
        elif isinstance(o, Decision):
            return {
                'account': o.account,
                'description': o.description,
                'variants': o.variants,
                'honest_variants': o.honest_variants,
                'outcome': o.outcome,
                'timestamp': o.timestamp
            }
        elif isinstance(o, ResultNode):
            return {
                'aggregation_summary': o.aggregation_summary,
                'transaction_log_collection': o.tx_collection,
                'children': [{
                    'decision': decision,
                    'child': child
                } for decision, child in o.children.items()],
            }
        elif isinstance(o, SimulationResult):
            return {
                'important_execution_results': o.get_important_execution_results(),
                'preparation_transactions': o.preparation_transactions,
                'execution_result_root': o.execution_result_root,
                'cleanup_transaction': o.cleanup_transactions,
            }
        elif isinstance(o, TransactionLogCollection):
            return {
                'aggregation': o.aggregation,
                'transaction_log_lists': o.tx_log_lists
            }
        elif isinstance(o, TransactionLogCollection.Aggregation):
            return list(o.entries.values())
        elif isinstance(o, TransactionLogCollection.Aggregation.Entry):
            return {
                'account': o.account,
                'tx_fees_min': o.tx_fees_min,
                'tx_fees_max': o.tx_fees_max,
                'tx_fees_mean': o.tx_fees_mean,
                'tx_count_min': o.tx_count_min,
                'tx_count_max': o.tx_count_max,
                'tx_count_mean': o.tx_count_mean,
                'funds_diff_min': o.funds_diff_min,
                'funds_diff_max': o.funds_diff_max,
                'count': o.list_count
            }
        elif isinstance(o, TransactionLogEntry):
            return {
                'account': o.account,
                'transaction': o.tx_dict,
                'transaction_receipt': o.tx_receipt,
                'funds_diffs': [{
                    'account': account,
                    'funds_diff': diff
                } for account, diff in o.funds_diff_collection.items()]
            }
        elif isinstance(o, TransactionLogList):
            return {
                'aggregation': o.aggregation,
                'transactions': o.tx_log_list
            }
        elif isinstance(o, TransactionLogList.Aggregation):
            return list(o.entries.values())
        elif isinstance(o, TransactionLogList.Aggregation.Entry):
            return {
                'account': o.account,
                'tx_fees': o.tx_fees,
                'tx_count': o.tx_count,
                'funds_diff': o.funds_diff
            }
        else:
            return super(JSONEncoder, self).default(o)


OutputFormatManager.register('json', JSONOutputFormat)
