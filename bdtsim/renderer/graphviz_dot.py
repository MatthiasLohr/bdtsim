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

import os
import tempfile
from typing import Any, Callable, List, NamedTuple, Optional, cast
from uuid import uuid4

from graphviz import Digraph  # type: ignore

from bdtsim.protocol_path import Decision
from bdtsim.simulation_result import SimulationResult, ResultNode, TransactionLogList, TransactionLogCollection, \
    TransactionLogEntry
from bdtsim.util.types import to_bool
from .renderer import Renderer, ValueType
from .renderer_manager import RendererManager


class GraphvizDotRenderer(Renderer):
    COLOR_HONEST = '#00CC00'
    COLOR_CHEATING = '#FF0000'

    def __init__(self, output_format: Optional[str] = None, graphviz_renderer: Optional[str] = None,
                 graphviz_formatter: Optional[str] = None, show_transactions: bool = True,
                 show_transaction_duplicates: bool = False, *args: Any, **kwargs: Any) -> None:
        """Create a [dot graph](https://www.graphviz.org/) for simulation result presentation.

        Args:
            wei_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed as well as
                Ethereum unit prefixes (Wei, GWei, Eth).
            gas_scaling (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be
                scaled. For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed.
            output_format: The output format used for rendering (``'pdf'``, ``'png'``, etc., defaults to
                ``None`` (dot raw source)).
            graphviz_renderer (Optional[str]): The output renderer used for rendering (``'cairo'``, ``'gd'``, ...).
            graphviz_formatter (Optional[str]): The output formatter used for rendering (``'cairo'``, ``'gd'``, ...).
            show_transactions (bool):
            show_transaction_duplicates(bool):
            *args (Any): Collector for unrecognized positional arguments
            **kwargs (Any): Collector for unrecognized keyword arguments
        """
        super(GraphvizDotRenderer, self).__init__(*args, **kwargs)
        self._output_format = output_format
        self._graphviz_renderer = graphviz_renderer
        self._graphviz_formatter = graphviz_formatter
        self._show_transactions = to_bool(show_transactions)
        self._show_transaction_duplicates = to_bool(show_transaction_duplicates)

    def render(self, simulation_result: SimulationResult) -> bytes:
        graph = ResultGraph(
            simulation_result=simulation_result,
            show_transactions=self._show_transactions,
            show_transaction_duplicates=self._show_transaction_duplicates,
            autoscale_func=self.autoscale
        )

        if self._output_format is None:
            return cast(bytes, graph.source.encode('utf-8')) + b'\n'
        else:
            tmp_dot_output_file = tempfile.mktemp()
            graph.render(
                filename=tmp_dot_output_file,
                format=self._output_format,
                renderer=self._graphviz_renderer,
                formatter=self._graphviz_formatter
            )
            with open(tmp_dot_output_file + '.' + self._output_format, 'rb') as fp:
                dot_output = fp.read()
            os.remove(tmp_dot_output_file)
            return dot_output


class NodeTemplate(object):
    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def generate(self, graph: Digraph) -> None:
        graph.node(self.name, *self.args, **self.kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NodeTemplate):
            return self.name == other.name and self.args == other.args and self.kwargs == self.kwargs
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class EdgeTemplate(object):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def generate(self, graph: Digraph) -> None:
        graph.edge(*self.args, **self.kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, EdgeTemplate):
            return self.args == other.args and self.kwargs == self.kwargs
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class TransactionPathPartTuple(NamedTuple):
    node_template: Optional[NodeTemplate]
    edge_template: EdgeTemplate

    def __eq__(self, other: Any) -> bool:
        if isinstance(self, TransactionPathPartTuple):
            if self.node_template is None and other.node_template is None:
                return True
            elif self.node_template is None:
                return False
            elif self.edge_template is None:
                return False
            return bool(self.node_template.args == other.node_template.args
                        and self.node_template.kwargs == other.node_template.kwargs)
        else:
            return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class ResultGraph(Digraph):  # type: ignore
    def __init__(self, simulation_result: SimulationResult, show_transactions: bool = False,
                 show_transaction_duplicates: bool = False,
                 autoscale_func: Optional[Callable[[Any, ValueType], Any]] = None) -> None:
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
        self._show_transaction_duplicates = show_transaction_duplicates
        self._autoscale_func = autoscale_func

        start_node_uuid = self._add_start_node()
        self._walk_result_nodes(start_node_uuid, simulation_result.execution_result_root)
        self._walk_preparation_nodes(simulation_result.preparation_transactions)
        self._walk_cleanup_nodes(simulation_result.cleanup_transactions)

    def _autoscale(self, value: Any, value_type: ValueType) -> Any:
        if self._autoscale_func is None:
            return value
        else:
            return self._autoscale_func(value, value_type)

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
        for tx_log_list in tx_collection:
            if len(tx_log_list) > 0:
                no_transactions_in_collection = False
                break

        if no_transactions_in_collection:
            return target_node_uuid

        # create start node
        transaction_start_uuid = self._add_transaction_node()

        # collect possible paths
        node_template: Optional[NodeTemplate]
        edge_template: EdgeTemplate
        transaction_graph_paths = []
        for tx_log_list in tx_collection:
            candidate_path = []
            prev_transaction_uuid = transaction_start_uuid
            for tx_log_entry in tx_log_list[:-1]:
                node_template = self._generate_transaction_node()
                edge_template = self._generate_transaction_edge(prev_transaction_uuid, node_template.name, tx_log_entry)
                candidate_path.append(TransactionPathPartTuple(node_template, edge_template))
                prev_transaction_uuid = node_template.name
            candidate_path.append(TransactionPathPartTuple(
                None,
                self._generate_transaction_edge(prev_transaction_uuid, target_node_uuid, tx_log_list[-1]))
            )
            if self._show_transaction_duplicates:
                transaction_graph_paths.append(candidate_path)
            else:
                if candidate_path not in transaction_graph_paths:
                    transaction_graph_paths.append(candidate_path)

        # generate actual nodes/edges
        for path in transaction_graph_paths:
            for node_template, edge_template in path[:-1]:
                if node_template is None:
                    raise RuntimeError('node_template should only be None in last element of path list')
                node_template.generate(self)
                edge_template.generate(self)
            path[-1][1].generate(self)

        return transaction_start_uuid

    def _walk_cleanup_nodes(self, transactions: TransactionLogList) -> None:
        self._walk_operator_nodes('Cleanup', transactions)

    def _walk_operator_nodes(self, phase: str, transactions: TransactionLogList) -> None:
        if len(transactions) == 0:
            return

        uuid = self._uuid()
        label = phase
        for entry in transactions.aggregation.values():
            label += '\n%s: %d (%d)' % (
                entry.account.name,
                self._autoscale(entry.tx_fees, ValueType.GAS),
                entry.tx_count
            )

        self.node(uuid, label, shape='box')

        if self._show_transactions:
            pass  # TODO add nodes for preparation/cleanup transactions

    def _add_start_node(self) -> str:
        uuid = self._uuid()
        self.node(uuid, label='<<b>Start</b>>', shape='circle', style='invis')
        return uuid

    def _add_decision_node(self, decision: Decision) -> str:
        uuid = self._uuid()
        label = '<%s<br /><b>%s</b>>' % (decision.choice.subject.name, decision.choice.description)
        self.node(uuid, label=label, shape='diamond')
        return uuid

    def _add_transaction_node(self) -> str:
        node_template = self._generate_transaction_node()
        node_template.generate(self)
        return node_template.name

    def _generate_transaction_node(self) -> NodeTemplate:
        return NodeTemplate(self._uuid(), label='', shape='circle', style='dotted')

    def _add_final_node(self, node: ResultNode) -> str:
        uuid = self._uuid()
        label_lines = []
        for entry in node.aggregation_summary.values():
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
        label = '<b>Start</b>'
        if not self._show_transactions:
            for line in self._get_label_lines_for_tx_collection(tx_collection):
                label += '<br/>%s' % str(line)

        self.edge(
            tail_name=src,
            head_name=dest,
            label='<%s>' % label
        )

    def _add_decision_edge(self, src: str, dest: str, decision: Decision,
                           tx_collection: TransactionLogCollection) -> None:
        label = '<b>%s</b>' % decision.outcome
        if not self._show_transactions:
            for line in self._get_label_lines_for_tx_collection(tx_collection):
                label += '<br />%s' % str(line)

        self.edge(
            tail_name=src,
            head_name=dest,
            label='<%s>' % label,
            color=self._color_by_honesty(decision.is_honest())
        )

    def _add_transaction_edge(self, src: str, dest: str, tx_log: TransactionLogEntry) -> None:
        edge_template = self._generate_transaction_edge(src, dest, tx_log)
        edge_template.generate(self)

    def _generate_transaction_edge(self, src: str, dest: str, tx_log: TransactionLogEntry) -> EdgeTemplate:
        label = '<b>%s: %s</b> (%s Gas, Bal. %s)' % (
            tx_log.account.name,
            tx_log.description or 'n.a.',
            self._autoscale(tx_log.tx_receipt['gasUsed'], ValueType.GAS),
            - self._autoscale(int(tx_log.tx_receipt['gasUsed']) * int(tx_log.tx_dict['gasPrice']), ValueType.WEI)
        )
        if not tx_log.funds_diff_collection.is_neutral:
            label += '<br/><b>Funds Diffs:</b>'
            for account, value in tx_log.funds_diff_collection.items():
                label += '<br />%s: %i' % (account.name, self._autoscale(value, ValueType.WEI))

        return EdgeTemplate(
            src,
            dest,
            label='<%s>' % label
        )

    @staticmethod
    def _uuid() -> str:
        return str(uuid4())

    @staticmethod
    def _color_by_honesty(honest: bool) -> str:
        return GraphvizDotRenderer.COLOR_HONEST if honest else GraphvizDotRenderer.COLOR_CHEATING

    @staticmethod
    def _get_label_lines_for_tx_collection(tx_collection: TransactionLogCollection) -> List[str]:
        return [str(entry) for entry in tx_collection.aggregation.values()]


RendererManager.register('dot', GraphvizDotRenderer)
