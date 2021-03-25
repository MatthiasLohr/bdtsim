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

from typing import Any, Callable, Optional

from graphviz import Digraph  # type: ignore

from bdtsim.protocol_path import Decision, Choice
from bdtsim.simulation_result import SimulationResult, ResultNode
from .graphviz_mixin import GraphvizMixin
from .renderer import Renderer, ValueType
from .renderer_manager import RendererManager


class GameTreeRenderer(Renderer, GraphvizMixin):
    def __init__(self, output_format: Optional[str] = None, graphviz_renderer: Optional[str] = None,
                 graphviz_formatter: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        Renderer.__init__(self, *args, **kwargs)
        self._output_format = output_format
        self._graphviz_renderer = graphviz_renderer
        self._graphviz_formatter = graphviz_formatter

    def render(self, simulation_result: SimulationResult) -> bytes:
        gt = SimulationGameTree(
            simulation_result=simulation_result,
            autoscale_func=self.autoscale
        )
        return self.render_graph(
            graph=gt,
            output_format=self._output_format,
            graphviz_renderer=self._graphviz_renderer,
            graphviz_formatter=self._graphviz_formatter
        )


class SimulationGameTree(Digraph):  # type: ignore
    def __init__(self, simulation_result: SimulationResult,
                 autoscale_func: Optional[Callable[[Any, ValueType], Any]] = None) -> None:
        super(SimulationGameTree, self).__init__(
            name='gametree',
            graph_attr={
                'fontname': 'Arial'
            },
            node_attr={
                'fontname': 'Arial'
            },
            edge_attr={
                'fontname': 'Arial'
            }
        )

        self._simulation_result = simulation_result
        self._autoscale_func = autoscale_func

        self._generated_node_count = 0
        self._generated_subgraph_count = 0
        self.attr(_attributes={
            'rankdir': 'LR',
            'splines': 'true'
        })

        self._render_simulation_result()

    def _autoscale(self, value: Any, value_type: ValueType) -> Any:
        if self._autoscale_func is None:
            return value
        else:
            return self._autoscale_func(value, value_type)

    def _render_simulation_result(self) -> None:
        self._process_node(self._simulation_result.execution_result_root)

    def _process_node(self, node: ResultNode) -> str:
        if len(node.children):
            # choice node
            choice = list(node.children.keys())[0].choice
            node_id = self._create_choice_node(choice)

            for child_decision, child_node in node.children.items():
                child_nid = self._process_node(child_node)
                self._create_decision_edge(node_id, child_nid, child_decision)
        else:
            node_id = self._create_final_node(node)

        return node_id

    def _create_unique_node_id(self) -> str:
        self._generated_node_count += 1
        return 'node_%d' % self._generated_node_count

    def _create_unique_subgraph_id(self) -> str:
        self._generated_subgraph_count += 1
        return 'cluster_%d' % self._generated_subgraph_count

    def _create_choice_node(self, choice: Choice) -> str:
        nid = self._create_unique_node_id()
        self.node(
            name=nid,
            shape='circle',
            label='',
            xlabel='<<b>%s</b><br/><i>%s</i>>' % (
                choice.subject.name,
                choice.description
            ),
            style='filled',
            fillcolor='black',
            width='0.15'
        )
        return nid

    def _create_final_node(self, node: ResultNode) -> str:
        # prepare label
        label_lines = []
        for subject in (self._simulation_result.seller, self._simulation_result.buyer):
            if node.account_completely_honest(subject):
                honesty_indicator = '<font color="green">✓</font>'
            else:
                honesty_indicator = '<font color="red">✗</font>'

            label_lines.append('<b>%s %s</b>' % (honesty_indicator, subject.name))
            aggregation_summary = node.aggregation_summary
            subject_summary = aggregation_summary.get(subject)

            for summary_label, summary_attr, summary_type in (
                ('TX Fees', 'tx_fees', ValueType.GAS),
                ('TX Count', 'tx_count', ValueType.PLAIN),
                ('Funds Diff', 'funds_diff', ValueType.WEI),
                ('Bal. Diff', 'balance_diff', ValueType.WEI),
                ('Item Share', 'item_share', ValueType.PLAIN)
            ):
                if subject_summary is None:
                    label_lines.append('<i>%s</i>: 0' % summary_label)
                else:
                    value_min = getattr(subject_summary, summary_attr + '_min')
                    value_max = getattr(subject_summary, summary_attr + '_max')
                    if value_min == value_max:
                        value_str = str(self._autoscale(value_min, summary_type))
                    else:
                        value_str = '[%s, %s]' % (
                            str(self._autoscale(value_min, summary_type)),
                            str(self._autoscale(value_max, summary_type))
                        )

                    label_lines.append('<i>%s</i>: %s' % (
                        summary_label,
                        value_str
                    ))

        # create dot node
        nid = self._create_unique_node_id()
        self.node(
            name=nid,
            shape='note',
            label='<%s>' % '<br/>'.join(label_lines)
        )
        return nid

    def _create_decision_edge(self, from_nid: str, to_nid: str, decision: Decision) -> None:
        color = 'blue' if decision.is_honest() else 'red'
        self.edge(
            tail_name=from_nid,
            head_name=to_nid,
            label=decision.outcome,
            color=color
        )


RendererManager.register('game-tree', GameTreeRenderer)
