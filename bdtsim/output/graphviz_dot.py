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
from typing import List, Optional
from uuid import uuid4

from graphviz import Digraph  # type: ignore

from bdtsim.protocol_path import Decision
from bdtsim.util.types import to_bool
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager
from .simulation_result import SimulationResult, ResultNode, TransactionLogList, TransactionLogCollection


class GraphvizDotOutputFormat(OutputFormat):
    COLOR_HONEST = '#00CC00'
    COLOR_CHEATING = '#FF0000'

    def __init__(self, output_filename: Optional[str] = None, view: bool = False, cleanup: bool = False,
                 output_format: str = 'pdf', graphviz_renderer: Optional[str] = None,
                 graphviz_formatter: Optional[str] = None, show_edges_details: Optional[bool] = True) -> None:
        """Create a [dot graph](https://www.graphviz.org/) for simulation result presentation.

        Args:
            output_filename (str): If provided, save dot graph to this file instead of printing to stdout
            view (bool): Open the rendered result with the default application (defaults to False).
            cleanup (bool): Delete the source file after rendering (defaults to False).
            output_format: The output format used for rendering (``'pdf'``, ``'png'``, etc., defaults to ``'pdf'``).
            graphviz_renderer: The output renderer used for rendering (``'cairo'``, ``'gd'``, ...).
            graphviz_formatter: The output formatter used for rendering (``'cairo'``, ``'gd'``, ...).
        """
        super(GraphvizDotOutputFormat, self).__init__()
        self._output_filename = output_filename
        self._view = to_bool(view)
        self._cleanup = cleanup
        self._output_format = output_format
        self._graphviz_renderer = graphviz_renderer
        self._graphviz_formatter = graphviz_formatter
        self._show_edges_details = to_bool(show_edges_details)

        if self._view and self._output_filename is None:
            self._output_filename = tempfile.mktemp(prefix='bdtsim-', suffix='.dot')

    def render(self, simulation_result: SimulationResult) -> None:
        graph = self._generate_graph(simulation_result)

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

    def _generate_graph(self, simulation_result: SimulationResult) -> Digraph:
        graph = Digraph(
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

        self._add_preparation_node(graph, simulation_result.preparation_transactions)
        self._add_cleanup_node(graph, simulation_result.cleanup_transactions)

        start_node_uuid = self._uuid()
        self._add_start_node(graph, start_node_uuid)
        self._walk_nodes(graph, simulation_result.execution_result_root, start_node_uuid, None)

        return graph

    def _add_preparation_node(self, graph: Digraph, tx_list: TransactionLogList) -> None:
        self._add_transaction_summaring_node(graph, 'Preparation', tx_list)

    def _add_cleanup_node(self, graph: Digraph, tx_list: TransactionLogList) -> None:
        self._add_transaction_summaring_node(graph, 'Cleanup', tx_list)

    @staticmethod
    def _add_transaction_summaring_node(graph: Digraph, title: str, tx_list: TransactionLogList) -> None:
        if len(tx_list) == 0:
            return

        label = title

        for entry in tx_list.aggregation.entries.values():
            label += '\n%s: %d (%d)' % (entry.account.name, entry.tx_fees, entry.tx_count)

        graph.node(title, label, shape='box')

    @staticmethod
    def _add_start_node(graph: Digraph, uuid: str) -> None:
        graph.node(uuid, label='<<b>Start</b>>')

    @staticmethod
    def _add_decision_node(graph: Digraph, uuid: str, label: str) -> None:
        graph.node(uuid, label=label, shape='diamond')

    def _add_start_edge(self, graph: Digraph, parent_uuid: str, child_uuid: str,
                        tx_collection: TransactionLogCollection) -> None:
        if self._show_edges_details:
            label = '<%s>' % ''.join(
                ['%s<br />' % str(label_line) for label_line in self._get_label_lines_for_tx_collection(tx_collection)]
            )
        else:
            label = ''

        graph.edge(
            tail_name=parent_uuid,
            head_name=child_uuid,
            label=label
        )

    def _add_decision_edge(self, graph: Digraph, parent_uuid: str, child_uuid: str, decision: Decision,
                           tx_collection: TransactionLogCollection) -> None:
        if self._show_edges_details:
            label_lines = self._get_label_lines_for_tx_collection(tx_collection)
            label = '<<b>%s</b><br />%s>' % (decision.outcome, ''.join(
                ['%s<br />' % str(line) for line in label_lines]
            ))
        else:
            label = '<<b>%s</b>>' % decision.outcome

        graph.edge(
            tail_name=parent_uuid,
            head_name=child_uuid,
            label=label,
            color=self._color_by_honesty(decision.is_honest())
        )

    @staticmethod
    def _get_label_lines_for_tx_collection(tx_collection: TransactionLogCollection) -> List[str]:
        return [str(entry) for entry in tx_collection.aggregation.entries.values()]

    def _add_end_node(self, graph: Digraph, uuid: str, node: ResultNode) -> None:
        label_lines = []
        for entry in node.aggregation_summary.entries.values():
            label_lines.append('<font color="%s">%s</font>' % (
                self._color_by_honesty(node.account_completely_honest(entry.account)),
                str(entry)
            ))

        graph.node(
            name=uuid,
            label='<<b>Total</b><br align="left" />%s<br align="left" />>' % '<br align="left" />'.join(label_lines),
            shape='box'
        )

    def _walk_nodes(self, graph: Digraph, current_node: ResultNode, parent_uuid: str,
                    incoming_decision: Optional[Decision]) -> None:
        current_node_uuid = self._uuid()

        if len(current_node.children) > 0:
            # Decision Node
            first_decision = list(current_node.children.keys())[0]
            current_node_label = '<%s<br /><b>%s</b>>' % (first_decision.account.name, first_decision.description)
            self._add_decision_node(graph, current_node_uuid, current_node_label)
        else:
            self._add_end_node(graph, current_node_uuid, current_node)

        if incoming_decision is not None:
            self._add_decision_edge(graph, parent_uuid, current_node_uuid, incoming_decision,
                                    current_node.tx_collection)
        else:
            self._add_start_edge(graph, parent_uuid, current_node_uuid, current_node.tx_collection)

        for decision, child_node in current_node.children.items():
            self._walk_nodes(graph, child_node, current_node_uuid, decision)

    @staticmethod
    def _uuid() -> str:
        return str(uuid4())

    @staticmethod
    def _color_by_honesty(honest: bool) -> str:
        return GraphvizDotOutputFormat.COLOR_HONEST if honest else GraphvizDotOutputFormat.COLOR_CHEATING


OutputFormatManager.register('dot', GraphvizDotOutputFormat)
