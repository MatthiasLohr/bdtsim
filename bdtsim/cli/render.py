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

import argparse
import sys
from typing import Dict, Optional

from bdtsim.renderer import RendererManager
from bdtsim.simulation_result import SimulationResultSerializer
from bdtsim.util.types import to_bool
from .command_manager import SubCommand


class RenderSubCommand(SubCommand):
    help = 'Render simulation result'

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        super(RenderSubCommand, self).__init__(parser)
        parser.add_argument('renderer', choices=RendererManager.renderers.keys(), help='Renderer to be used')
        parser.add_argument('-i', '--input', default='-', help='Input file to be used, default: stdin')
        parser.add_argument('--input-compression', default=True)
        parser.add_argument('--input-b64encoding', default=True)
        parser.add_argument('-o', '--output', default='-', help='Output file to be used, default: stdout')
        parser.add_argument('-p', '--parameter', nargs=2, action='append', dest='parameters',
                            default=[], metavar=('KEY', 'VALUE'), help='additional parameters for the renderer')

    def __call__(self, args: argparse.Namespace) -> Optional[int]:
        # prepare parameters
        parameters: Dict[str, str] = {}
        for key, value in args.parameters:
            parameters[key.replace('-', '_')] = value

        # instantiate renderer
        renderer = RendererManager.instantiate(
            args.renderer,
            **parameters
        )

        # load input data
        if args.input == '-':
            data = sys.stdin.buffer.read()
        else:
            with open(args.input, 'rb') as fp:
                data = fp.read()

        serializer = SimulationResultSerializer(
            compression=to_bool(args.input_compression),
            b64encoding=to_bool(args.input_b64encoding)
        )

        simulation_result = serializer.unserialize(data)

        # render output
        renderer.render(simulation_result)

        return 0
