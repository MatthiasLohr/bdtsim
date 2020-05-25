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

from typing import Dict, Optional

from bdtsim.account import Account, seller, buyer
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager
from .simulation_result import SimulationResult, TransactionLogList, TransactionLogCollection


class HumanReadableOutputFormat(OutputFormat):
    def __init__(self) -> None:
        super(HumanReadableOutputFormat, self).__init__()

    @staticmethod
    def _print_list_aggregation_entries(entries: Dict[Account, TransactionLogList.Aggregation.Entry]) -> None:
        for entry in entries.values():
            print('%s: %d (%d)' % (entry.account.name, entry.tx_fees, entry.tx_count))
        print('')

    @staticmethod
    def _print_collection_aggregation_entries(
            entries: Dict[Account, TransactionLogCollection.Aggregation.Entry]) -> None:
        for entry in entries.values():
            print(str(entry))
        print('')

    @staticmethod
    def _maximize_collection_aggregation_attribute(current: Optional[TransactionLogCollection.Aggregation],
                                                   new: TransactionLogCollection.Aggregation, account: Account,
                                                   attribute: str) -> Optional[TransactionLogCollection.Aggregation]:
        current_entry = None
        current_value = None
        if current is not None:
            current_entry = current.entries.get(account)
        if current_entry is not None:
            current_value = getattr(current_entry, attribute)

        new_entry = new.entries.get(account)
        new_value = None
        if new_entry is not None:
            new_value = getattr(new_entry, attribute)

        if current_entry is None:
            if new_entry is not None:
                return new
            else:
                return None
        else:  # current_entry is NOT None
            if new_entry is not None:
                if current_value is not None and new_value is not None:
                    if new_value > current_value:
                        return new
                    else:
                        return current
                else:
                    raise RuntimeError()
            else:
                return current

    def render(self, simulation_result: SimulationResult) -> None:
        if len(simulation_result.preparation_transactions.aggregation.entries) > 0:
            print('=== Preparation Costs:')
            self._print_list_aggregation_entries(simulation_result.preparation_transactions.aggregation.entries)

        final_nodes = simulation_result.execution_result_root.final_nodes
        all_account_honest_agg_sum = None
        buyer_honest_max_fees_agg_sum = None
        seller_honest_max_fees_agg_sum = None

        for node in final_nodes:
            if node.all_accounts_completely_honest():
                all_account_honest_agg_sum = node.aggregation_summary
            elif node.account_completely_honest(buyer) and not node.account_completely_honest(seller):
                buyer_honest_max_fees_agg_sum = self._maximize_collection_aggregation_attribute(
                    current=buyer_honest_max_fees_agg_sum,
                    new=node.aggregation_summary,
                    account=buyer,
                    attribute='tx_fees_max'
                )
            elif node.account_completely_honest(seller) and not node.account_completely_honest(buyer):
                seller_honest_max_fees_agg_sum = self._maximize_collection_aggregation_attribute(
                    current=seller_honest_max_fees_agg_sum,
                    new=node.aggregation_summary,
                    account=seller,
                    attribute='tx_fees_max'
                )
            else:
                pass  # ignore both cheating cases

        print('=== All Participants honest:')
        if all_account_honest_agg_sum is not None:
            self._print_collection_aggregation_entries(all_account_honest_agg_sum.entries)

        print('=== Honest Seller max Costs with cheating Buyer:')
        if seller_honest_max_fees_agg_sum is not None:
            self._print_collection_aggregation_entries(seller_honest_max_fees_agg_sum.entries)

        print('=== Honest Buyer max Costs with cheating Seller:')
        if buyer_honest_max_fees_agg_sum is not None:
            self._print_collection_aggregation_entries(buyer_honest_max_fees_agg_sum.entries)

        if len(simulation_result.cleanup_transactions.aggregation.entries) > 0:
            print('=== Cleanup Costs:')
            self._print_list_aggregation_entries(simulation_result.cleanup_transactions.aggregation.entries)


OutputFormatManager.register('human-readable', HumanReadableOutputFormat)
