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

import tempfile
from typing import Any, List, Optional, Union
from uuid import uuid4

from graphviz import Digraph  # type: ignore

from bdtsim.protocol_path import Decision
from bdtsim.simulation_result import SimulationResult, ResultNode, TransactionLogList, TransactionLogCollection, \
    TransactionLogEntry
from bdtsim.util.types import to_bool
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager


class GraphvizDotOutputFormat(OutputFormat):
    COLOR_HONEST = '#00CC00'
    COLOR_CHEATING = '#FF0000'

    def __init__(self, wei_scaling: Union[int, float, str] = 1, gas_scaling: Union[int, float, str] = 1,
                 output_filename: Optional[str] = None, view: bool = False, cleanup: bool = False,
                 output_format: str = 'pdf', graphviz_renderer: Optional[str] = None,
                 graphviz_formatter: Optional[str] = None, show_transactions: Optional[bool] = True, *args: Any,
                 **kwargs: Any) -> None:
        """Create a [dot graph](https://www.graphviz.org/) for simulation result presentation.

        Args:
            wei_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed as well as
                Ethereum unit prefixes (Wei, GWei, Eth).
            gas_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed.
            output_filename (str): If provided, save dot graph to this file instead of printing to stdout
            view (bool): Open the rendered result with the default application (defaults to False).
            cleanup (bool): Delete the source file after rendering (defaults to False).
            output_format: The output format used for rendering (``'pdf'``, ``'png'``, etc., defaults to ``'pdf'``).
            graphviz_renderer: The output renderer used for rendering (``'cairo'``, ``'gd'``, ...).
            graphviz_formatter: The output formatter used for rendering (``'cairo'``, ``'gd'``, ...).
            *args (Any): Collector for unrecognized positional arguments
            **kwargs (Any): Collector for unrecognized keyword arguments
        """
        super(GraphvizDotOutputFormat, self).__init__(wei_scaling, gas_scaling, *args, **kwargs)
        self._output_filename = output_filename
        self._view = to_bool(view)
        self._cleanup = cleanup
        self._output_format = output_format
        self._graphviz_renderer = graphviz_renderer
        self._graphviz_formatter = graphviz_formatter
        self._show_transactions = to_bool(show_transactions)

        if self._view and self._output_filename is None:
            self._output_filename = tempfile.mktemp(prefix='bdtsim-', suffix='.dot')

    def render(self, simulation_result: SimulationResult) -> None:
        graph = ResultGraph(simulation_result, self._show_transactions)

        if self._output_filename is not None:
            graph.render(
                filename=self._output_filename,
                view=self._view,
                cleanup=self._cleanup,
                format=self._output_format,
                renderer=self._graphviz_renderer,
                formatter=self._graphviz_formatter
            )
        else:
            print(graph.source)


class ResultGraph(Digraph):  # type: ignore
    def __init__(self, simulation_result: SimulationResult, show_transactions: bool = False) -> None:
        super(ResultGraph, self).__init__(
            graph_attr=[
                ('rankdir', 'LR'),
                ('fontname', 'helvetica')
            ],
            node_attr=[
                ('fontname', 'helvetica')
            ],
            edge_attr=[
                ('fontname', 'helvetica')
            ]
        )

        self._show_transactions = show_transactions

        start_node_uuid = self._add_start_node()
        self._walk_result_nodes(start_node_uuid, simulation_result.execution_result_root)
        self._walk_preparation_nodes(simulation_result.preparation_transactions)
        self._walk_cleanup_nodes(simulation_result.preparation_transactions)

    def _walk_preparation_nodes(self, transactions: TransactionLogList) -> None:
        self._walk_operator_nodes('Preparation', transactions)

    def _walk_result_nodes(self, parent_uuid: str, current_node: ResultNode,
                           incoming_decision: Optional[Decision] = None) -> None:
        if len(current_node.children) > 0:  # it's a decision node
            current_node_decision = list(current_node.children.keys())[0]
            current_node_uuid = self._add_decision_node(current_node_decision)
        else:  # it's a final node
            current_node_uuid = self._add_final_node(current_node)

        target_node_uuid = self._walk_transaction_nodes(current_node_uuid, current_node.tx_collection)

        if incoming_decision is not None:
            self._add_decision_edge(parent_uuid, target_node_uuid, incoming_decision, current_node.tx_collection)
        else:
            self._add_start_edge(parent_uuid, target_node_uuid, current_node.tx_collection)

        for decision, child_node in current_node.children.items():
            self._walk_result_nodes(current_node_uuid, child_node, decision)

    def _walk_transaction_nodes(self, target_node_uuid: str, tx_collection: TransactionLogCollection) -> str:
        if not self._show_transactions:
            return target_node_uuid

        no_transactions_in_collection = True
        for tx_log_list in tx_collection.tx_log_lists:
            if len(tx_log_list) > 0:
                no_transactions_in_collection = False
                break

        if no_transactions_in_collection:
            return target_node_uuid

        transaction_start_uuid = self._add_transaction_node()
        for tx_log_list in tx_collection.tx_log_lists:
            prev_transaction_uuid = transaction_start_uuid
            for tx_log_entry in tx_log_list.tx_log_list[:-1]:
                transaction_node_uuid = self._add_transaction_node()
                self._add_transaction_edge(prev_transaction_uuid, transaction_node_uuid, tx_log_entry)
                prev_transaction_uuid = transaction_node_uuid
            self._add_transaction_edge(prev_transaction_uuid, target_node_uuid, tx_log_list.tx_log_list[-1])
        return transaction_start_uuid

    def _walk_cleanup_nodes(self, transactions: TransactionLogList) -> None:
        self._walk_operator_nodes('Cleanup', transactions)

    def _walk_operator_nodes(self, phase: str, transactions: TransactionLogList) -> None:
        if len(transactions) == 0:
            return

        uuid = self._uuid()
        label = phase
        for entry in transactions.aggregation.entries.values():
            label += '\n%s: %d (%d)' % (entry.account.name, entry.tx_fees, entry.tx_count)

        self.node(uuid, label, shape='box')

        if self._show_transactions:
            pass  # TODO add nodes for preparation/cleanup transactions

    def _add_start_node(self) -> str:
        uuid = self._uuid()
        self.node(uuid, label='<<b>Start</b>>', shape='circle', style='invis')
        return uuid

    def _add_decision_node(self, decision: Decision) -> str:
        uuid = self._uuid()
        label = '<%s<br /><b>%s</b>>' % (decision.account.name, decision.description)
        self.node(uuid, label=label, shape='diamond')
        return uuid

    def _add_transaction_node(self) -> str:
        uuid = self._uuid()
        self.node(uuid, label='', shape='circle', style='dotted')
        return uuid

    def _add_final_node(self, node: ResultNode) -> str:
        uuid = self._uuid()
        label_lines = []
        for entry in node.aggregation_summary.entries.values():
            label_lines.append('<font color="%s">%s</font>' % (
                self._color_by_honesty(node.account_completely_honest(entry.account)),
                str(entry)
            ))

        self.node(
            name=uuid,
            label='<<b>Total</b><br align="left" />%s<br align="left" />>' % '<br align="left" />'.join(label_lines),
            shape='box'
        )

        return uuid

    def _add_start_edge(self, src: str, dest: str, tx_collection: TransactionLogCollection) -> None:
        label = '<%s>' % ''.join(
            ['%s<br />' % str(label_line) for label_line in self._get_label_lines_for_tx_collection(tx_collection)]
        )

        self.edge(
            tail_name=src,
            head_name=dest,
            label=label
        )

    def _add_decision_edge(self, src: str, dest: str, decision: Decision,
                           tx_collection: TransactionLogCollection) -> None:
        label_lines = self._get_label_lines_for_tx_collection(tx_collection)
        label = '<<b>%s</b><br />%s>' % (decision.outcome, ''.join(
            ['%s<br />' % str(line) for line in label_lines]
        ))

        self.edge(
            tail_name=src,
            head_name=dest,
            label=label,
            color=self._color_by_honesty(decision.is_honest())
        )

    def _add_transaction_edge(self, src: str, dest: str, tx_log: TransactionLogEntry) -> None:
        label = '<b>%s: %s</b> (%s Gas)' % (
            tx_log.account.name,
            tx_log.description or 'n.a.',
            tx_log.tx_receipt['gasUsed']
        )
        if not tx_log.funds_diff_collection.is_neutral:
            label += '<br/><b>Funds Diffs:</b>'
            for account, value in tx_log.funds_diff_collection.items():
                label += '<br />%s: %i' % (account.name, value)

        self.edge(
            tail_name=src,
            head_name=dest,
            label='<%s>' % label
        )

    @staticmethod
    def _uuid() -> str:
        return str(uuid4())

    @staticmethod
    def _color_by_honesty(honest: bool) -> str:
        return GraphvizDotOutputFormat.COLOR_HONEST if honest else GraphvizDotOutputFormat.COLOR_CHEATING

    @staticmethod
    def _get_label_lines_for_tx_collection(tx_collection: TransactionLogCollection) -> List[str]:
        return [str(entry) for entry in tx_collection.aggregation.entries.values()]


OutputFormatManager.register('dot', GraphvizDotOutputFormat)
