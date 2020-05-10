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

from typing import Any, Dict, List, Optional

from bdtsim.account import Account
from bdtsim.protocol_path import Decision


class TransactionLogEntry(object):
    def __init__(self, account: Account, tx_dict: Dict[str, Any], tx_receipt: Dict[str, Any]) -> None:
        self.account = account
        self.tx_dict = tx_dict
        self.tx_receipt = tx_receipt


class TransactionLogAggregation(object):
    class Result(object):
        def __init__(self, account: Account, tx_fees: int, tx_count: int):
            self.account = account
            self.tx_fees = tx_fees
            self.tx_count = tx_count

    def __init__(self, tx_logs: List[TransactionLogEntry]):
        self._tx_logs = tx_logs

        self._aggregation_results: Optional[List['TransactionLogAggregation.Result']] = None

    @property
    def transactions(self) -> List[TransactionLogEntry]:
        return self._tx_logs

    @property
    def aggregation_results(self) -> List['TransactionLogAggregation.Result']:
        if self._aggregation_results is None:
            tx_fees: Dict[Account, List[int]] = {}

            for tx in self._tx_logs:
                slot = tx_fees.get(tx.account)
                if slot is None:
                    tx_fees.update({tx.account: [tx.tx_receipt['gasUsed']]})
                else:
                    slot.append(tx.tx_receipt['gasUsed'])

            self._aggregation_results = [
                TransactionLogAggregation.Result(account, sum(slot), len(slot)) for account, slot in tx_fees.items()
            ]

        return self._aggregation_results

    def get_aggregation_for_account(self, account: Account) -> Optional['TransactionLogAggregation.Result']:
        for result in self.aggregation_results:
            if result.account == account:
                return result
        return None


class ResultNode(object):
    def __init__(self, parent: Optional['ResultNode'] = None):
        self.parent = parent
        self.children: Dict[Decision, ResultNode] = {}
        self.transactions: List[List[TransactionLogEntry]] = []

    def child(self, decision: Decision) -> 'ResultNode':
        child = self.children.get(decision)
        if child is None:
            child = ResultNode(self)
            self.children.update({decision: child})
        return child


class SimulationResult(object):
    def __init__(self) -> None:
        self.preparation_transactions: List[TransactionLogEntry] = []
        self.execution_result_root = ResultNode()
        self.cleanup_transactions: List[TransactionLogEntry] = []
