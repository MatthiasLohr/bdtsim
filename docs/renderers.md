# Renderers

This page describes supported renderers for the [`bdtsim render`](commands.md#render) command.
[`bdtsim render`](commands.md#render) takes an existing simulation result file and converts it
to an interpretable format, such as readable CLI output or graphs.

The following renderers are currently available:

  * [dot](#dot)
  * [game matrix](#game-matrix)
  * [game-tree](#game-tree)


## General Options

The following parameters are available for all renderers:

  * `wei-scaling` (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be scaled.
    For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed as well as Ethereum unit prefixes (Wei, GWei, Eth).
  * `gas-scaling` (Union[int, float, str]): If int/float provided, it will be multiplied with the value to be scaled.
    For str, common unit prefixes (https://en.wikipedia.org/wiki/Unit_prefix) are allowed.


## Renderers

### dot

Create a [dot graph](https://www.graphviz.org/) for simulation result presentation.
Please note: the `dot` binary (graphviz package) needs to be available on your system.

```
# Print dot sources
bdtsim render dot -i simulation.result

# Write to file and convert to PNG
bdtsim render dot -p output-filename /tmp/bdtsim.dot -p output-format png -i simulation.result
```

#### Parameters

  * `output-filename` (str): If provided, save dot graph to this file instead of printing to stdout
  * `view` (bool): Open the rendered result with the default application (defaults to False).
  * `cleanup` (bool): Delete the source file after rendering (defaults to False).
  * `output-format`: The output format used for rendering (`'pdf'`, `'png'`, etc., defaults to `'pdf'`).
  * `graphviz-renderer`: The output renderer used for rendering (`'cairo'`, `'gd'`, ...).
  * `graphviz-formatter`: The output formatter used for rendering (`'cairo'`, `'gd'`, ...). 


### game-matrix

Create a human-readable ASCII art table which contains the relevant output parameters in a comparable way.

```
bdtsim game-matrix dot -i simulation.result
```

#### Parameters

*No additional parameters supported*

### game-tree

Create a game tree (using [graphviz dot](https://www.graphviz.org/)
Please note: the `dot` binary (graphviz package) needs to be available on your system.

```
# print dot source to stdout
bdtsim game-tree dot -i simulation.result

# generate PDF file containing game tree graph
bdtsim render game-tree -i simulation.result | dot -Tpdf -o game-tree.pdf
```

#### Parameters

*No additional parameters supported*
