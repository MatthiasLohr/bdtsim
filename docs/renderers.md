# Renderers

This page describes supported renderers for the [`bdtsim render`](commands.md#render) command.
[`bdtsim render`](commands.md#render) takes an existing simulation result file and converts it
to an interpretable format, such as readable CLI output or graphs.

The following renderers are currently available:

## human-readable

Renders the results in a human-readable form.

```
bdtsim render human-readable -i simulation.result
```

### Parameters

No additional parameters available.


## dot

Create a [dot graph](https://www.graphviz.org/) for simulation result presentation.

```
# Print dot sources
bdtsim render dot -i simulation.result

# Write to file and convert to PNG
bdtsim render dot -p output-filename /tmp/bdtsim.dot -p output-format png -i simulation.result
```

### Parameters

  * `output-filename` (str): If provided, save dot graph to this file instead of printing to stdout
  * `view` (bool): Open the rendered result with the default application (defaults to False).
  * `cleanup` (bool): Delete the source file after rendering (defaults to False).
  * `output-format`: The output format used for rendering (`'pdf'`, `'png'`, etc., defaults to `'pdf'`).
  * `graphviz-renderer`: The output renderer used for rendering (`'cairo'`, `'gd'`, ...).
  * `graphviz-formatter`: The output formatter used for rendering (`'cairo'`, `'gd'`, ...). 
