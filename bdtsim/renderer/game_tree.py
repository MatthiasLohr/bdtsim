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

import sys

from graphviz import Digraph  # type: ignore

from bdtsim.protocol_path import Decision
from bdtsim.simulation_result import SimulationResult, ResultNode
from .renderer import Renderer
from .renderer_manager import RendererManager


class GameTreeRenderer(Renderer):
    def render(self, simulation_result: SimulationResult) -> None:
        gt = GameTreeGraph()
        gt.render_simulation_result(simulation_result)
        sys.stdout.write(gt.source + '\n')


class GameTreeGraph(Digraph):  # type: ignore
    def __init__(self) -> None:
        super(GameTreeGraph, self).__init__(
            graph_attr={
                'rankdir': 'TB'
            }
        )
        self._generated_node_count = 0
        self._generated_subgraph_count = 0

    def render_simulation_result(self, simulation_result: SimulationResult) -> None:
        start_nid = self._create_start_node()
        self._process_child_nodes(simulation_result.execution_result_root, start_nid)

    def _process_child_nodes(self, parent_node: ResultNode, parent_nid: str) -> None:
        if len(parent_node.children) > 0:
            # this is a decision node
            subgraph_id = self._create_unique_subgraph_id()
            decision_sub_graph = Digraph(
                name=subgraph_id,
                graph_attr={
                }
            )

            for child_decision, child_node in parent_node.children.items():
                child_nid = self._create_intermediary_node(decision_sub_graph)
                self._create_decision_edge(parent_nid, child_nid, child_decision)
                self._process_child_nodes(child_node, child_nid)

            self.subgraph(decision_sub_graph)
        else:
            # this is a final node
            pass

    def _create_unique_node_id(self) -> str:
        self._generated_node_count += 1
        return 'gametree_node_%d' % self._generated_node_count

    def _create_unique_subgraph_id(self) -> str:
        self._generated_subgraph_count += 1
        return 'gametree_subgraph_%d' % self._generated_subgraph_count

    def _create_start_node(self) -> str:
        return self._create_intermediary_node(self)

    def _create_intermediary_node(self, graph: Digraph) -> str:
        nid = self._create_unique_node_id()
        graph.node(nid, '', shape='point')
        return str(nid)

    def _create_decision_edge(self, nid_source: str, nid_target: str, decision: Decision) -> None:
        self.edge(
            tail_name=nid_source,
            head_name=nid_target,
            label=decision.outcome
        )


RendererManager.register('game-tree', GameTreeRenderer)
