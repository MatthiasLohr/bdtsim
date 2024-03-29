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

import base64
import copy
import gzip
import itertools
import logging
import pickle
import uuid
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, cast

from bdtsim.account import Account
from bdtsim.account_related_diff_collection import FundsDiffCollection, ItemShareCollection
from bdtsim.protocol_path import Decision


logger = logging.getLogger(__name__)


class TransactionLogEntry(NamedTuple):
    """Log entry and according information of a single transaction"""
    account: Account
    tx_dict: Dict[str, Any]
    tx_receipt: Dict[str, Any]
    description: str
    funds_diff_collection: FundsDiffCollection
    item_share_collection: ItemShareCollection

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TransactionLogEntry):
            return (self.account == other.account and
                    self.tx_dict == other.tx_dict and
                    self.tx_receipt == other.tx_receipt and
                    self.description == other.description and
                    self.funds_diff_collection == other.funds_diff_collection and
                    self.item_share_collection == other.item_share_collection)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class TransactionLogList(List[TransactionLogEntry]):
    """List of TransactionLogEntry"""
    class Aggregation(Dict[Account, 'TransactionLogList.Aggregation.Entry']):
        class Entry(NamedTuple):
            account: Account
            tx_fees: int
            tx_count: int
            funds_diff: int
            balance_diff: int
            item_share: float

            def __str__(self) -> str:
                return '%s: %d (%d transaction(s), funds diff %d, balance diff %d, item share %d)' % (
                    self.account.name,
                    self.tx_fees,
                    self.tx_count,
                    self.funds_diff,
                    self.balance_diff,
                    self.item_share
                )

        def __init__(self, tx_log_list: 'TransactionLogList') -> None:
            super(TransactionLogList.Aggregation, self).__init__()
            for tx in tx_log_list:
                # work on log line
                entry = self.get(tx.account)
                if entry is None:
                    entry = TransactionLogList.Aggregation.Entry(
                        tx.account,                                                       # account
                        int(tx.tx_receipt['gasUsed']),                                    # tx_fees
                        1,                                                                # tx_count
                        0,                                                                # funds_diff
                        - (int(tx.tx_receipt['gasUsed']) * int(tx.tx_dict['gasPrice'])),  # balance_diff
                        0                                                                 # item_share
                    )
                    self.update({tx.account: entry})
                else:
                    entry = TransactionLogList.Aggregation.Entry(
                        tx.account,
                        entry.tx_fees + int(tx.tx_receipt['gasUsed']),
                        entry.tx_count + 1,
                        entry.funds_diff,
                        entry.balance_diff - (int(tx.tx_receipt['gasUsed']) * int(tx.tx_dict['gasPrice'])),
                        entry.item_share
                    )
                    self.update({tx.account: entry})
                # work on all fund diffs
                for account, funds_diff in tx.funds_diff_collection.items():
                    funds_diff_entry = self.get(account)
                    if funds_diff_entry is None:
                        self.update({
                            account: TransactionLogList.Aggregation.Entry(
                                account,
                                0,
                                0,
                                funds_diff,
                                funds_diff,
                                0
                            )
                        })
                    else:
                        self.update({
                            account: TransactionLogList.Aggregation.Entry(
                                account,
                                entry.tx_fees,
                                entry.tx_count,
                                funds_diff_entry.funds_diff + funds_diff,
                                entry.balance_diff + funds_diff,
                                entry.item_share
                            )
                        })
                # work on all item shares
                for account, item_share in tx.item_share_collection.items():
                    item_share_entry = self.get(account)
                    if item_share_entry is None:
                        self.update({
                            account: TransactionLogList.Aggregation.Entry(
                                account,
                                0,
                                0,
                                0,
                                0,
                                item_share
                            )
                        })
                    else:
                        self.update({
                            account: TransactionLogList.Aggregation.Entry(
                                account,
                                entry.tx_fees,
                                entry.tx_count,
                                entry.funds_diff,
                                entry.balance_diff,
                                item_share_entry.item_share + item_share
                            )
                        })

    def __init__(self) -> None:
        super(TransactionLogList, self).__init__()
        self._aggregation: Optional[TransactionLogList.Aggregation] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TransactionLogList):
            return super(TransactionLogList, self).__eq__(other)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @property
    def aggregation(self) -> 'TransactionLogList.Aggregation':
        if self._aggregation is None:
            self._aggregation = TransactionLogList.Aggregation(self)
        return self._aggregation


class TransactionLogCollection(List[TransactionLogList]):
    class Aggregation(Dict[Account, 'TransactionLogCollection.Aggregation.Entry']):
        class Entry(NamedTuple):
            account: Account
            tx_fees_min: int
            tx_fees_max: int
            tx_fees_mean: float
            tx_count_min: int
            tx_count_max: int
            tx_count_mean: float
            funds_diff_min: int
            funds_diff_max: int
            balance_diff_min: int
            balance_diff_max: int
            item_share_min: float
            item_share_max: float

            def __str__(self) -> str:
                if self.tx_fees_min == self.tx_fees_max:
                    tx_fees_str = ' %d' % self.tx_fees_min
                else:
                    tx_fees_str = ' %d/%d/%d' % (self.tx_fees_min, round(self.tx_fees_mean), self.tx_fees_max)

                if self.tx_count_min == self.tx_count_max:
                    tx_count_str = '%d transaction(s)' % self.tx_count_min
                else:
                    tx_count_str = '%d/%d/%d transaction(s)' % (
                        self.tx_count_min,
                        round(self.tx_count_mean, 1),
                        self.tx_count_max
                    )

                if self.funds_diff_min == self.funds_diff_max:
                    funds_diff_str = 'funds diff %d' % self.funds_diff_min
                else:
                    funds_diff_str = 'funds diff %d/%d' % (self.funds_diff_min, self.funds_diff_max)

                if self.balance_diff_min == self.balance_diff_max:
                    balance_diff_str = 'balance diff %d' % self.balance_diff_min
                else:
                    balance_diff_str = 'balance diff %d/%d' % (self.balance_diff_min, self.balance_diff_max)

                if self.item_share_min == self.item_share_max:
                    item_share_str = 'item share %d' % self.item_share_min
                else:
                    item_share_str = 'item share %d/%d' % (self.item_share_min, self.item_share_max)

                return '%s: %s (%s, %s, %s, %s)' % (
                    self.account.name,
                    tx_fees_str,
                    tx_count_str,
                    funds_diff_str,
                    balance_diff_str,
                    item_share_str
                )

        def __init__(self, tx_log_collection: 'TransactionLogCollection') -> None:
            super(TransactionLogCollection.Aggregation, self).__init__()
            for tx_log_list in tx_log_collection:
                for tx_list_aggregation_entry in tx_log_list.aggregation.values():
                    e = self.get(tx_list_aggregation_entry.account)
                    if e is None:
                        self.update({tx_list_aggregation_entry.account: TransactionLogCollection.Aggregation.Entry(
                            account=tx_list_aggregation_entry.account,
                            tx_fees_min=tx_list_aggregation_entry.tx_fees,
                            tx_fees_max=tx_list_aggregation_entry.tx_fees,
                            tx_fees_mean=tx_list_aggregation_entry.tx_fees / len(tx_log_collection),
                            tx_count_min=tx_list_aggregation_entry.tx_count,
                            tx_count_max=tx_list_aggregation_entry.tx_count,
                            tx_count_mean=tx_list_aggregation_entry.tx_count / len(tx_log_collection),
                            funds_diff_min=tx_list_aggregation_entry.funds_diff,
                            funds_diff_max=tx_list_aggregation_entry.funds_diff,
                            balance_diff_min=tx_list_aggregation_entry.balance_diff,
                            balance_diff_max=tx_list_aggregation_entry.balance_diff,
                            item_share_min=tx_list_aggregation_entry.item_share,
                            item_share_max=tx_list_aggregation_entry.item_share
                        )})
                    else:
                        self.update({tx_list_aggregation_entry.account: TransactionLogCollection.Aggregation.Entry(
                            account=tx_list_aggregation_entry.account,
                            tx_fees_min=min(e.tx_fees_min, tx_list_aggregation_entry.tx_fees),
                            tx_fees_max=max(e.tx_fees_max, tx_list_aggregation_entry.tx_fees),
                            tx_fees_mean=e.tx_fees_mean + (tx_list_aggregation_entry.tx_fees / len(tx_log_collection)),
                            tx_count_min=min(e.tx_count_min, tx_list_aggregation_entry.tx_count),
                            tx_count_max=max(e.tx_count_max, tx_list_aggregation_entry.tx_count),
                            tx_count_mean=e.tx_count_mean + tx_list_aggregation_entry.tx_count / len(tx_log_collection),
                            funds_diff_min=min(e.funds_diff_min, tx_list_aggregation_entry.funds_diff),
                            funds_diff_max=max(e.funds_diff_max, tx_list_aggregation_entry.funds_diff),
                            balance_diff_min=min(e.balance_diff_min, tx_list_aggregation_entry.balance_diff),
                            balance_diff_max=max(e.balance_diff_max, tx_list_aggregation_entry.balance_diff),
                            item_share_min=min(e.item_share_min, tx_list_aggregation_entry.item_share),
                            item_share_max=max(e.item_share_max, tx_list_aggregation_entry.item_share)
                        )})

        def __iadd__(self, other: 'TransactionLogCollection.Aggregation') -> 'TransactionLogCollection.Aggregation':
            if isinstance(other, TransactionLogCollection.Aggregation):
                for remote_entry in other.values():
                    local_entry = self.get(remote_entry.account)
                    if local_entry is None:
                        self.update({remote_entry.account: copy.deepcopy(remote_entry)})
                    else:
                        self.update({remote_entry.account: TransactionLogCollection.Aggregation.Entry(
                            account=remote_entry.account,
                            tx_fees_min=local_entry.tx_fees_min + remote_entry.tx_fees_min,
                            tx_fees_max=local_entry.tx_fees_max + remote_entry.tx_fees_max,
                            tx_fees_mean=local_entry.tx_fees_mean + remote_entry.tx_fees_mean,
                            tx_count_min=local_entry.tx_count_min + remote_entry.tx_count_min,
                            tx_count_max=local_entry.tx_count_max + remote_entry.tx_count_max,
                            tx_count_mean=local_entry.tx_count_mean + remote_entry.tx_count_mean,
                            funds_diff_min=local_entry.funds_diff_min + remote_entry.funds_diff_min,
                            funds_diff_max=local_entry.funds_diff_max + remote_entry.funds_diff_max,
                            balance_diff_min=local_entry.balance_diff_min + remote_entry.balance_diff_min,
                            balance_diff_max=local_entry.balance_diff_max + remote_entry.balance_diff_max,
                            item_share_min=local_entry.item_share_min + remote_entry.item_share_min,
                            item_share_max=local_entry.item_share_max + remote_entry.item_share_max
                        )})
                return self
            else:
                return NotImplemented

    def __init__(self, tx_log_lists: Optional[List[TransactionLogList]] = None) -> None:
        super(TransactionLogCollection, self).__init__()
        self._aggregation: Optional[TransactionLogCollection.Aggregation] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TransactionLogCollection):
            return super(TransactionLogCollection, self).__eq__(other)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

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
        self._uuid = uuid.uuid4()

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
            if incoming_decision.choice.subject == account and not incoming_decision.is_honest():
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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ResultNode):
            return self._uuid == other._uuid
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class AggregationAttributeHelper(object):
    def __init__(self, account: Account, attribute: str) -> None:
        self._account = account
        self._attribute = attribute

    def __call__(self, aggregation: TransactionLogCollection.Aggregation) -> Any:
        return getattr(aggregation.get(self._account), self._attribute)


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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SimulationResult):
            return (self.preparation_transactions == other.preparation_transactions and
                    self.execution_result_root == other.execution_result_root and
                    self.cleanup_transactions == other.cleanup_transactions and
                    self.operator == other.operator and
                    self.seller == other.seller and
                    self.buyer == other.buyer)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @staticmethod
    def _apply_aggr_func(aggr_func: Callable[..., TransactionLogCollection.Aggregation],
                         results: List[TransactionLogCollection.Aggregation], account: Account,
                         attribute: str) -> Optional[TransactionLogCollection.Aggregation]:
        results_filtered = list(filter(lambda x: x.get(account) is not None, results))
        if len(results_filtered) == 0:
            return None
        return aggr_func(results_filtered, key=AggregationAttributeHelper(account, attribute))


class SimulationResultSerializer(object):
    def __init__(self, compression: bool = True, b64encoding: bool = True):
        self._compression = compression
        self._b64encoding = b64encoding

    def serialize(self, simulation_result: 'SimulationResult') -> bytes:
        result_bytes = pickle.dumps(simulation_result, protocol=4)
        if self._compression:
            result_bytes = gzip.compress(result_bytes)
        if self._b64encoding:
            result_bytes = base64.encodebytes(result_bytes)
        return result_bytes

    def unserialize(self, data: bytes) -> 'SimulationResult':
        if self._b64encoding:
            data = base64.decodebytes(data)
        if self._compression:
            data = gzip.decompress(data)
        return cast(SimulationResult, pickle.loads(data))
