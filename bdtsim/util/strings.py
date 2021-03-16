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

from typing import List


def str_block_table(blocks: List[List[str]], column_separator: str = '|', row_separator: str = '-',
                    line_crossing: str = '+') -> str:
    if column_separator == '' or row_separator == '':
        line_crossing = ''

    # analyze
    row_count = len(blocks)
    column_count = max(len(row) for row in blocks)
    blocks_splitted = [[block.split() for block in row] for row in blocks]
    row_heights = [
        max([len(block_splitted) for block_splitted in row_splitted]) for row_splitted in blocks_splitted
    ]
    column_widths = [
        max([
            max([len(line) for line in row_splitted[column_index]]) for row_splitted in blocks_splitted
        ]) for column_index in range(column_count)
    ]

    print(row_heights, column_widths)

    # generate
    output = ''
    for row_index in range(row_count):
        if row_index > 0:
            output += '\n'
            if not row_separator == '':
                output += line_crossing.join([row_separator * width for width in column_widths]) + '\n'

        row_height = row_heights[row_index]
        for line_index in range(row_height):
            if line_index > 0:
                output += '\n'

            for column_index in range(column_count):
                if column_index > 0:
                    output += column_separator

                if line_index >= len(blocks_splitted[row_index][column_index]):
                    output += ' ' * column_widths[column_index]
                else:
                    output += blocks_splitted[row_index][column_index][line_index].ljust(column_widths[column_index])

    return output
