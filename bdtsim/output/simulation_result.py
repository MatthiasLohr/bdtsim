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

import copy
import itertools
from typing import Any, Callable, Dict, List, Optional, Tuple

from bdtsim.account import Account
from bdtsim.funds_diff_collection import FundsDiffCollection
from bdtsim.protocol_path import Decision


class TransactionLogEntry(object):
    def __init__(self, account: Account, tx_dict: Dict[str, Any], tx_receipt: Dict[str, Any],
                 funds_diff_collection: FundsDiffCollection) -> None:
        self.account = account
        self.tx_dict = tx_dict
        self.tx_receipt = tx_receipt
        self.funds_diff_collection = funds_diff_collection


class TransactionLogList(object):
    class Aggregation(object):
        class Entry(object):
            def __init__(self, account: Account, tx_fees: int, tx_count: int, funds_diff: int) -> None:
                self.account = account
                self.tx_fees = tx_fees
                self.tx_count = tx_count
                self.funds_diff = funds_diff

            def __str__(self) -> str:
                return '%s: %d (%d transaction(s), value diff %d)' % (
                    self.account.name,
                    self.tx_fees,
                    self.tx_count,
                    self.funds_diff
                )

        def __init__(self, tx_list: 'TransactionLogList') -> None:
            self.entries: Dict[Account, TransactionLogList.Aggregation.Entry] = {}
            for tx in tx_list.tx_log_list:
                # work on log line
                entry = self.entries.get(tx.account)
                if entry is None:
                    self.entries.update({
                        tx.account: TransactionLogList.Aggregation.Entry(
                            tx.account,
                            int(tx.tx_receipt['gasUsed']),
                            1,
                            0
                        )
                    })
                else:
                    entry.tx_fees += int(tx.tx_receipt['gasUsed'])
                    entry.tx_count += 1
                # work on all fund diffs
                for account, funds_diff in tx.funds_diff_collection.items():
                    funds_diff_entry = self.entries.get(account)
                    if funds_diff_entry is None:
                        self.entries.update({
                            account: TransactionLogList.Aggregation.Entry(
                                account,
                                0,
                                0,
                                funds_diff
                            )
                        })
                    else:
                        funds_diff_entry.funds_diff += funds_diff

    def __init__(self) -> None:
        self.tx_log_list: List[TransactionLogEntry] = []
        self._aggregation: Optional[TransactionLogList.Aggregation] = None

    def __len__(self) -> int:
        return len(self.tx_log_list)

    def append(self, entry: TransactionLogEntry) -> None:
        return self.tx_log_list.append(entry)

    @property
    def aggregation(self) -> 'TransactionLogList.Aggregation':
        if self._aggregation is None:
            self._aggregation = TransactionLogList.Aggregation(self)
        return self._aggregation


class TransactionLogCollection(object):
    class Aggregation(object):
        class Entry(object):
            def __init__(self, account: Account, tx_fees_min: int, tx_fees_max: int, tx_fees_sum: int,
                         tx_count_min: int, tx_count_max: int, tx_count_sum: int, funds_diff_min: int,
                         funds_diff_max: int, list_count: int, ) -> None:
                self.account = account
                self.tx_fees_min = tx_fees_min
                self.tx_fees_max = tx_fees_max
                self.tx_fees_sum = tx_fees_sum
                self.tx_count_min = tx_count_min
                self.tx_count_max = tx_count_max
                self.tx_count_sum = tx_count_sum
                self.funds_diff_min = funds_diff_min
                self.funds_diff_max = funds_diff_max
                self.list_count = list_count

            def __str__(self) -> str:
                if self.tx_fees_min == self.tx_fees_max:
                    return '%s: %d (%d transaction(s), value diff %d)' % (
                        self.account.name,
                        self.tx_fees_min,
                        self.tx_count_min,
                        self.funds_diff_min
                    )
                else:
                    return '%s: %d/%d/%d (%d/%d/%d transaction(s), value diff %d/%d)' % (
                        self.account.name,
                        self.tx_fees_min, self.tx_fees_mean, self.tx_fees_max,
                        self.tx_count_min, self.tx_count_mean, self.tx_count_max,
                        self.funds_diff_min, self.funds_diff_max
                    )

            @property
            def tx_fees_mean(self) -> float:
                return self.tx_fees_sum / self.list_count

            @property
            def tx_count_mean(self) -> float:
                return self.tx_count_sum / self.list_count

        def __init__(self, tx_collection: 'TransactionLogCollection') -> None:
            self.entries: Dict[Account, TransactionLogCollection.Aggregation.Entry] = {}
            for tx_list in tx_collection.tx_log_lists:
                for tx_list_aggregation in tx_list.aggregation.entries.values():
                    entry = self.entries.get(tx_list_aggregation.account)
                    if entry is None:
                        self.entries.update({tx_list_aggregation.account: TransactionLogCollection.Aggregation.Entry(
                            tx_list_aggregation.account,
                            tx_list_aggregation.tx_fees,
                            tx_list_aggregation.tx_fees,
                            tx_list_aggregation.tx_fees,
                            tx_list_aggregation.tx_count,
                            tx_list_aggregation.tx_count,
                            tx_list_aggregation.tx_count,
                            tx_list_aggregation.funds_diff,
                            tx_list_aggregation.funds_diff,
                            1
                        )})
                    else:
                        entry.tx_fees_min = min(entry.tx_fees_min, tx_list_aggregation.tx_fees)
                        entry.tx_fees_max = max(entry.tx_fees_max, tx_list_aggregation.tx_fees)
                        entry.tx_fees_sum += tx_list_aggregation.tx_fees
                        entry.tx_count_min = min(entry.tx_count_min, tx_list_aggregation.tx_count)
                        entry.tx_count_max = max(entry.tx_count_max, tx_list_aggregation.tx_count)
                        entry.tx_count_sum += tx_list_aggregation.tx_count
                        entry.funds_diff_min = min(entry.funds_diff_min, tx_list_aggregation.funds_diff)
                        entry.funds_diff_max = max(entry.funds_diff_max, tx_list_aggregation.funds_diff)
                        entry.list_count += 1

        def __iadd__(self, other: 'TransactionLogCollection.Aggregation') -> 'TransactionLogCollection.Aggregation':
            if isinstance(other, TransactionLogCollection.Aggregation):
                for remote_entry in other.entries.values():
                    local_entry = self.entries.get(remote_entry.account)
                    if local_entry is None:
                        self.entries.update({remote_entry.account: copy.deepcopy(remote_entry)})
                    else:
                        local_entry.tx_fees_min += remote_entry.tx_fees_min
                        local_entry.tx_fees_max += remote_entry.tx_fees_max
                        local_entry.tx_fees_sum += remote_entry.tx_fees_sum
                        local_entry.tx_count_min += remote_entry.tx_count_min
                        local_entry.tx_count_max += remote_entry.tx_count_max
                        local_entry.tx_count_sum += remote_entry.tx_count_sum
                        local_entry.funds_diff_min += remote_entry.funds_diff_min
                        local_entry.funds_diff_max += remote_entry.funds_diff_max
                        local_entry.list_count += remote_entry.list_count
                return self
            else:
                return NotImplemented

    def __init__(self, tx_log_lists: Optional[List[TransactionLogList]] = None) -> None:
        self.tx_log_lists: List[TransactionLogList] = tx_log_lists or []
        self._aggregation: Optional[TransactionLogCollection.Aggregation] = None

    def __len__(self) -> int:
        return len(self.tx_log_lists)

    def append(self, entry: TransactionLogList) -> None:
        self.tx_log_lists.append(entry)

    @property
    def aggregation(self) -> 'TransactionLogCollection.Aggregation':
        if self._aggregation is None:
            self._aggregation = TransactionLogCollection.Aggregation(self)
        return self._aggregation


class ResultNode(object):
    def __init__(self, parent: Optional['ResultNode'] = None):
        self.parent = parent
        self.children: Dict[Decision, ResultNode] = {}
        self.tx_collection: TransactionLogCollection = TransactionLogCollection()

    def child(self, decision: Decision) -> 'ResultNode':
        child = self.children.get(decision)
        if child is None:
            child = ResultNode(self)
            self.children.update({decision: child})
        return child

    def all_accounts_completely_honest(self) -> bool:
        if self.parent is not None:
            incoming_decision = list(self.parent.children.keys())[list(self.parent.children.values()).index(self)]
            if not incoming_decision.is_honest():
                return False
            else:
                return self.parent.all_accounts_completely_honest()
        else:
            return True

    def account_completely_honest(self, account: Account) -> bool:
        if self.parent is not None:
            incoming_decision = list(self.parent.children.keys())[list(self.parent.children.values()).index(self)]
            if incoming_decision.account == account and not incoming_decision.is_honest():
                return False
            else:
                return self.parent.account_completely_honest(account)
        else:
            return True

    @property
    def final_nodes(self) -> List['ResultNode']:
        if len(self.children) > 0:
            return list(itertools.chain.from_iterable([c.final_nodes for c in self.children.values()]))
        else:
            return [self]

    @property
    def aggregation_summary(self) -> TransactionLogCollection.Aggregation:
        aggregation_summary = TransactionLogCollection.Aggregation(TransactionLogCollection())
        next_node: Optional[ResultNode] = self
        while next_node is not None:
            aggregation_summary += next_node.tx_collection.aggregation
            next_node = next_node.parent
        return aggregation_summary


class AggregationAttributeHelper(object):
    def __init__(self, account: Account, attribute: str) -> None:
        self._account = account
        self._attribute = attribute

    def __call__(self, aggregation: TransactionLogCollection.Aggregation) -> Any:
        return getattr(aggregation.entries.get(self._account), self._attribute)


class SimulationResult(object):
    def __init__(self, operator: Account, seller: Account, buyer: Account) -> None:
        self.preparation_transactions = TransactionLogList()
        self.execution_result_root = ResultNode()
        self.cleanup_transactions = TransactionLogList()
        self.operator = operator
        self.seller = seller
        self.buyer = buyer

    def get_important_execution_results(self) -> List[Tuple[str, TransactionLogCollection.Aggregation]]:
        all_honest_results = []
        seller_honest_results = []
        buyer_honest_results = []
        nobody_honest_results = []

        for node in self.execution_result_root.final_nodes:
            if node.all_accounts_completely_honest():
                all_honest_results.append(node.aggregation_summary)
            elif node.account_completely_honest(self.seller):
                seller_honest_results.append(node.aggregation_summary)
            elif node.account_completely_honest(self.buyer):
                buyer_honest_results.append(node.aggregation_summary)
            else:
                nobody_honest_results.append(node.aggregation_summary)

        important_results = []
        for honesty_str, results in [
            ('All Parties Honest', all_honest_results),
            ('Honest Seller, Cheating Buyer', seller_honest_results),
            ('Cheating Seller, Honest Buyer', buyer_honest_results),
            ('Cheating Seller, Cheating Buyer', buyer_honest_results)
        ]:
            for account in self.seller, self.buyer:
                tx_fees_max_result = self._apply_aggr_func(max, results, account, 'tx_fees_max')
                if tx_fees_max_result is not None:
                    important_results.append(('%s - %s max fees' % (honesty_str, account.name), tx_fees_max_result))

            profit_max_result = self._apply_aggr_func(max, results, self.seller, 'funds_diff_max')
            if profit_max_result is not None:
                important_results.append(('%s - Seller max profit' % honesty_str, profit_max_result))

            expenses_max_result = self._apply_aggr_func(min, results, self.buyer, 'funds_diff_min')
            if expenses_max_result is not None:
                important_results.append(('%s - Buyer max expenses' % honesty_str, expenses_max_result))

        return important_results

    @staticmethod
    def _apply_aggr_func(aggr_func: Callable[..., TransactionLogCollection.Aggregation],
                         results: List[TransactionLogCollection.Aggregation], account: Account,
                         attribute: str) -> Optional[TransactionLogCollection.Aggregation]:
        results_filtered = list(filter(lambda x: x.entries.get(account) is not None, results))
        if len(results_filtered) == 0:
            return None
        return aggr_func(results_filtered, key=AggregationAttributeHelper(account, attribute))
