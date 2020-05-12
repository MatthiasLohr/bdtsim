# Output Formats

This page describes supported output format for the [`bdtsim run`](commands.md#run) command.

## human-readable

Output the results in a human readable form.

```
bdtsim run SimplePayment PyEVM -f human-readable
```

### Parameters

No output format parameters available.

## dot

Create a [dot graph](https://www.graphviz.org/) for simulation result präsentation.

```
# Print dot sources
bdtsim run SimplePayment PyEVM -f dot

# Write to file and convert to PNG
bdtsim run SimplePayment PyEVM -f dot -o output-filename /tmp/bdtsim.dot -o output-format png
```

### Parameters

  * `output-filename` (str): If provided, save dot graph to this file instead of printing to stdout
  * `view` (bool): Open the rendered result with the default application (defaults to False).
  * `cleanup` (bool): Delete the source file after rendering (defaults to False).
  * `output-format`: The output format used for rendering (`'pdf'`, `'png'`, etc., defaults to `'pdf'`).
  * `graphviz-renderer`: The output renderer used for rendering (`'cairo'`, `'gd'`, ...).
  * `graphviz-formatter`: The output formatter used for rendering (`'cairo'`, `'gd'`, ...). 

## json

Output the simulation results in JSON.

```
bdtsim run SimplePayment PyEVM -f json
```

### Parameters

No output format parameters available.

## yaml

Output the simulation results in YAML.

```
bdtsim run SimplePayment PyEVM -f yaml
```

### Parameters

No output format parameters available.
