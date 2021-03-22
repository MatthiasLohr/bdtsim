# Renderers

This page describes supported renderers for the [`bdtsim render`](commands.md#render) command.
[`bdtsim render`](commands.md#render) takes an existing simulation result file and converts it
to an interpretable format, such as readable CLI output or graphs.

The following renderers are currently available:

  * [dot](#dot)
  * [game matrix](#game-matrix)
  * [game-tree](#game-tree)


## General Renderer Parameters

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
bdtsim render dot -o simulation.png -p output-format png -i simulation.result
```

#### Parameters

  * `output-format` (Optional[str]): The output format used for rendering. Supports any output format which is supported
    by graphviz (see https://graphviz.org/doc/info/output.html for a list of supported formats). With `None`, the dot
    source code will be returned. Defaults to `None`
  * `graphviz-renderer` (Optional[str]): The graphviz renderer used for rendering (see [graphviz docs](https://graphviz.org/documentation/))
  * `graphviz-formatter` (Optional[str]): The graphviz formatter used for rendering (see [graphviz docs](https://graphviz.org/documentation/))
  * `show_transactions` (bool): Add transactions edges to graph. Defaults to `True`
  * `show_transaction_duplicates` (bool): Add multiple edges for identical transaction. Defaults to `False`


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

  * `output-format` (Optional[str]): The output format used for rendering. Supports any output format which is supported
    by graphviz (see https://graphviz.org/doc/info/output.html for a list of supported formats). With `None`, the dot
    source code will be returned. Defaults to `None`
  * `graphviz-renderer` (Optional[str]): The graphviz renderer used for rendering (see [graphviz docs](https://graphviz.org/documentation/))
  * `graphviz-formatter` (Optional[str]): The graphviz formatter used for rendering (see [graphviz docs](https://graphviz.org/documentation/))
