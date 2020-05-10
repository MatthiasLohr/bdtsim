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

from statistics import mean
from typing import List, Optional
from uuid import uuid4

from graphviz import Digraph  # type: ignore

from bdtsim.account import Account
from bdtsim.protocol_path import Decision
from .output_format import OutputFormat
from .output_format_manager import OutputFormatManager
from .simulation_result import SimulationResult, ResultNode, TransactionLogEntry, TransactionLogAggregation


class GraphvizDotOutputFormat(OutputFormat):
    def __init__(self, output_file: Optional[str] = None, view: Optional[bool] = False) -> None:
        super(GraphvizDotOutputFormat, self).__init__()
        self._output_file = output_file
        self._view = view

    def render(self, simulation_result: SimulationResult) -> None:
        graph = self._generate_graph(simulation_result)

        if self._output_file is not None:
            graph.render('/tmp/bdtsim-output.svg', view=self._view)
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

    def _add_preparation_node(self, graph: Digraph, tx_logs: List[TransactionLogEntry]) -> None:
        self._add_transaction_summaring_node(graph, 'Preparation', tx_logs)

    def _add_cleanup_node(self, graph: Digraph, tx_logs: List[TransactionLogEntry]) -> None:
        self._add_transaction_summaring_node(graph, 'Cleanup', tx_logs)

    @staticmethod
    def _add_transaction_summaring_node(graph: Digraph, title: str, tx_logs: List[TransactionLogEntry]) -> None:
        if len(tx_logs) == 0:
            return

        label = title

        for line in TransactionLogAggregation(tx_logs).aggregation_results:
            label += '\n%s: %d (%d)' % (line.account.name, line.tx_fees, line.tx_count)
        graph.node(title, label, shape='box')

    @staticmethod
    def _add_start_node(graph: Digraph, uuid: str) -> None:
        graph.node(uuid, label='Start')

    @staticmethod
    def _add_decision_node(graph: Digraph, uuid: str, label: str) -> None:
        graph.node(uuid, label=label, shape='diamond')

    def _add_start_edge(self, graph: Digraph, parent_uuid: str, child_uuid: str,
                        transactions: List[List[TransactionLogEntry]]) -> None:
        graph.edge(parent_uuid, child_uuid, self._get_label_for_transactions(transactions).strip())

    def _add_decision_edge(self, graph: Digraph, parent_uuid: str, child_uuid: str, decision: Decision,
                           transactions: List[List[TransactionLogEntry]]) -> None:
        label = '%s' % decision.variant
        label += '\n' + self._get_label_for_transactions(transactions).strip()
        graph.edge(parent_uuid, child_uuid, label=label)

    @staticmethod
    def _get_label_for_transactions(tx_log_collection: List[List[TransactionLogEntry]]) -> str:
        aggregations = [TransactionLogAggregation(tx_logs) for tx_logs in tx_log_collection]
        accounts: List[Account] = []
        for aggregation in aggregations:
            for aggregation_result in aggregation.aggregation_results:
                if aggregation_result.account not in accounts:
                    accounts.append(aggregation_result.account)

        result = ''
        for account in accounts:
            account_aggregations = []
            for aggregation in aggregations:
                account_aggregation = aggregation.get_aggregation_for_account(account)
                if account_aggregation is not None:
                    account_aggregations.append(account_aggregation)

            result += '\n%s: %d/%d/%d (%d/%d/%d)' % (
                account.name,
                min([a.tx_fees for a in account_aggregations]),
                mean([a.tx_fees for a in account_aggregations]),
                max([a.tx_fees for a in account_aggregations]),
                min([a.tx_count for a in account_aggregations]),
                mean([a.tx_count for a in account_aggregations]),
                max([a.tx_count for a in account_aggregations]),
            )
        return result

    @staticmethod
    def _add_end_node(graph: Digraph, uuid: str) -> None:
        label = ('Operator Fees: %d/%d/%d (%d)\n'
                 'Seller Fees: %d/%d/%d (%d)\n'
                 'Seller Risk: %d\n'
                 'Buyer Fees: %d/%d/%d (%d)\n'
                 'Buyer Risk: %d') % (
            0, 0, 0, 0,
            0, 0, 0, 0,
            0,
            0, 0, 0, 0,
            0
        )

        graph.node(uuid, label=label, shape='box')

    def _walk_nodes(self, graph: Digraph, current_node: ResultNode, parent_uuid: str,
                    incoming_decision: Optional[Decision]) -> None:
        current_node_uuid = self._uuid()

        if len(current_node.children) > 0:
            # Decision Node
            first_decision = list(current_node.children.keys())[0]
            current_node_label = '%s:\n%s' % (first_decision.account.name, first_decision.description)
            self._add_decision_node(graph, current_node_uuid, current_node_label)
        else:
            self._add_end_node(graph, current_node_uuid)

        if incoming_decision is not None:
            self._add_decision_edge(graph, parent_uuid, current_node_uuid, incoming_decision, current_node.transactions)
        else:
            self._add_start_edge(graph, parent_uuid, current_node_uuid, current_node.transactions)

        for decision, child_node in current_node.children.items():
            self._walk_nodes(graph, child_node, current_node_uuid, decision)

    @staticmethod
    def _uuid() -> str:
        return str(uuid4())


OutputFormatManager.register('dot', GraphvizDotOutputFormat)
