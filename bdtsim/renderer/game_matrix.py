# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2021 Matthias Lohr <mail@mlohr.com>
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

from math import ceil
from typing import Any, Generator, List, Optional, Tuple

from bdtsim.account import Account
from bdtsim.simulation_result import SimulationResult, TransactionLogCollection
from bdtsim.util.strings import str_block_table
from .renderer import Renderer
from .renderer_manager import RendererManager


class GameMatrixAccountCell(object):
    def __init__(self, account: Account, tx_fees: Optional[Tuple[int, int]] = None,
                 tx_count: Optional[Tuple[int, int]] = None, funds_diff: Optional[Tuple[int, int]] = None,
                 balance_diff: Optional[Tuple[int, int]] = None) -> None:
        self._account = account
        self._tx_fees = tx_fees
        self._tx_count = tx_count
        self._funds_diff = funds_diff
        self._balance_diff = balance_diff

    @property
    def account(self) -> Account:
        return self._account

    @property
    def tx_fees(self) -> Optional[Tuple[int, int]]:
        return self._tx_fees

    @property
    def funds_diff(self) -> Optional[Tuple[int, int]]:
        return self._funds_diff

    @property
    def balance_diff(self) -> Optional[Tuple[int, int]]:
        return self._balance_diff

    def __str__(self) -> str:
        results = []
        for label, interval in (
            ('TX Fees', self._tx_fees),
            ('TX Count', self._tx_count),
            ('Funds Diff', self._funds_diff),
            ('Bal. Diff', self._balance_diff)
        ):
            if interval is None:
                results.append('%s: 0' % label)
            else:
                if interval[0] == interval[1]:
                    results.append('%s: %d' % (label, interval[0]))
                else:
                    results.append('%s: [%d, %d]' % (label, interval[0], interval[1]))

        return '\n'.join(results)

    @staticmethod
    def from_aggregation_summary_list(aggregation_summary_list: List[TransactionLogCollection.Aggregation],
                                      account: Account) -> 'GameMatrixAccountCell':
        def _safe_attr_generator(attr_name: str) -> Generator[Any, None, None]:
            for entry in aggregation_summary_list:
                item = entry.get(account)
                if item is not None:
                    yield getattr(item, attr_name)

        if len(aggregation_summary_list):
            return GameMatrixAccountCell(
                account=account,
                tx_fees=(
                    min(_safe_attr_generator('tx_fees_min')),
                    max(_safe_attr_generator('tx_fees_max'))
                ),
                tx_count=(
                    min(_safe_attr_generator('tx_count_min')),
                    max(_safe_attr_generator('tx_count_max'))
                ),
                funds_diff=(
                    min(_safe_attr_generator('funds_diff_min')),
                    max(_safe_attr_generator('funds_diff_max'))
                ),
                balance_diff=(
                    min(_safe_attr_generator('balance_diff_min')),
                    max(_safe_attr_generator('balance_diff_max'))
                ),
            )
        else:
            return GameMatrixAccountCell(account=account)


class GameMatrixCell(object):
    def __init__(self, seller_cell: GameMatrixAccountCell, buyer_cell: GameMatrixAccountCell) -> None:
        self._seller_cell = seller_cell
        self._buyer_cell = buyer_cell

    @property
    def seller_cell(self) -> GameMatrixAccountCell:
        return self._seller_cell

    @property
    def buyer_cell(self) -> GameMatrixAccountCell:
        return self._buyer_cell

    @staticmethod
    def from_aggregation_summary_list(aggregation_summary_list: List[TransactionLogCollection.Aggregation],
                                      seller: Account, buyer: Account) -> 'GameMatrixCell':
        return GameMatrixCell(
            seller_cell=GameMatrixAccountCell.from_aggregation_summary_list(
                aggregation_summary_list=list(filter(
                    lambda item: item.get(seller) is not None,
                    aggregation_summary_list
                )),
                account=seller
            ),
            buyer_cell=GameMatrixAccountCell.from_aggregation_summary_list(
                aggregation_summary_list=list(filter(
                    lambda item: item.get(buyer) is not None,
                    aggregation_summary_list
                )),
                account=buyer
            )
        )


class GameMatrix(object):
    def __init__(self, seller: Account, buyer: Account, cell_hh: GameMatrixCell, cell_hm: GameMatrixCell,
                 cell_mh: GameMatrixCell, cell_mm: GameMatrixCell) -> None:
        self._seller = seller
        self._buyer = buyer
        self._cell_hh = cell_hh
        self._cell_hm = cell_hm
        self._cell_mh = cell_mh
        self._cell_mm = cell_mm

    def __str__(self) -> str:
        seller_honest_tbl_half_str = str_block_table(
            blocks=[
                [str(self._cell_hh.seller_cell), str(self._cell_hh.buyer_cell)],
                [str(self._cell_hm.seller_cell), str(self._cell_hm.buyer_cell)]
            ],
            column_separator=' │ ',
            line_crossing='─┼─',
            row_separator='─'
        )
        seller_malicious_tbl_half_str = str_block_table(
            blocks=[
                [str(self._cell_hh.seller_cell), str(self._cell_hh.buyer_cell)],
                [str(self._cell_hm.seller_cell), str(self._cell_hm.buyer_cell)]
            ],
            column_separator=' │ ',
            line_crossing='─┼─',
            row_separator='─'
        )
        values_tbl_str = str_block_table(
            blocks=[[seller_honest_tbl_half_str, seller_malicious_tbl_half_str]],
            column_separator=' ║ ',
            row_separator='─'
        )

        prefix_width = len(self._buyer.name) + 2  # +2 for ' ✓' and ' ✗'
        values_width = len(values_tbl_str.split('\n')[0])
        values_height = len(values_tbl_str.split('\n'))
        value_row_height = (values_height - 1) / 2
        symbol_height = ceil(value_row_height / 2) - 1
        buyer_str_height = ceil(values_height / 2) - 1
        seller_honest_tbl_half_width = len(seller_honest_tbl_half_str.split('\n')[0])
        seller_malicious_tbl_half_width = len(seller_malicious_tbl_half_str.split('\n')[0])
        buyer_tbl_str = (
            ('\n' * symbol_height)
            + ' ' * len(self._buyer.name)
            + ' ✓'
            + ('\n' * (buyer_str_height - symbol_height))
            + self._buyer.name + '  \n'
            + ('\n' * symbol_height)
            + ' ' * len(self._buyer.name)
            + ' ✗'
        )

        # puzzle together the output parts
        output = (
            (' ' * prefix_width)
            + ' ║ '
            + self._seller.name.center(values_width)
        )
        output += (
            '\n'
            + (' ' * prefix_width)
            + ' ║ '
            + '✓'.center(seller_honest_tbl_half_width)
            + ' '
            + '✗'.center(seller_malicious_tbl_half_width)
        )
        output += (
            '\n'
            + ('═' * prefix_width)
            + '═╬═'
            + ('═' * values_width)
        )
        output += '\n' + str_block_table(
            blocks=[[buyer_tbl_str, values_tbl_str]],
            column_separator=' ║ '
        )
        return output

    @staticmethod
    def from_simulation_result(simulation_result: SimulationResult) -> 'GameMatrix':
        # initialize aggregation summary lists
        asl_hh = []
        asl_hm = []
        asl_mh = []
        asl_mm = []

        for final_node in simulation_result.execution_result_root.final_nodes:
            seller_honest = final_node.account_completely_honest(simulation_result.seller)
            buyer_honest = final_node.account_completely_honest(simulation_result.buyer)

            if seller_honest and buyer_honest:
                asl_hh.append(final_node.aggregation_summary)
            elif seller_honest and not buyer_honest:
                asl_hm.append(final_node.aggregation_summary)
            elif not seller_honest and buyer_honest:
                asl_mh.append(final_node.aggregation_summary)
            elif not seller_honest and not buyer_honest:
                asl_mm.append(final_node.aggregation_summary)
            else:
                raise RuntimeError('Should be impossible to reach hear! Please contact developers.')

        return GameMatrix(
            seller=simulation_result.seller,
            buyer=simulation_result.buyer,
            cell_hh=GameMatrixCell.from_aggregation_summary_list(
                aggregation_summary_list=asl_hh,
                seller=simulation_result.seller,
                buyer=simulation_result.buyer
            ),
            cell_hm=GameMatrixCell.from_aggregation_summary_list(
                aggregation_summary_list=asl_hm,
                seller=simulation_result.seller,
                buyer=simulation_result.buyer
            ),
            cell_mh=GameMatrixCell.from_aggregation_summary_list(
                aggregation_summary_list=asl_mh,
                seller=simulation_result.seller,
                buyer=simulation_result.buyer
            ),
            cell_mm=GameMatrixCell.from_aggregation_summary_list(
                aggregation_summary_list=asl_mm,
                seller=simulation_result.seller,
                buyer=simulation_result.buyer
            )
        )


class GameMatrixRenderer(Renderer):
    def render(self, simulation_result: SimulationResult) -> None:
        game_matrix = GameMatrix.from_simulation_result(simulation_result)
        print(game_matrix)


RendererManager.register('game-matrix', GameMatrixRenderer)
