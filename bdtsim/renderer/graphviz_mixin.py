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

import os
import tempfile
from typing import Optional, cast

from graphviz import Digraph  # type: ignore


class GraphvizMixin(object):
    @staticmethod
    def render_graph(graph: Digraph, output_format: Optional[str] = None, graphviz_renderer: Optional[str] = None,
                     graphviz_formatter: Optional[str] = None) -> bytes:
        if output_format is None:
            return cast(bytes, graph.source.encode('utf-8')) + b'\n'
        else:
            tmp_dot_output_fp, tmp_dot_output_filename = tempfile.mkstemp()
            graph.render(
                filename=tmp_dot_output_filename,
                format=output_format,
                renderer=graphviz_renderer,
                formatter=graphviz_formatter
            )
            with open(tmp_dot_output_filename + '.' + output_format, 'rb') as fp:
                dot_output = fp.read()
            os.remove(tmp_dot_output_filename)
            return dot_output
