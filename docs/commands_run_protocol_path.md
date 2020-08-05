# run --protocol-path

With the `--protocol-path` parameter it is possible to limit the simulation to certain protocol paths.
This can be done by defining decision outcomes, to which the simulation is then limited.

## Syntax

The `--protocol-path` parameter expects a comma seperated list of decision outcomes,
one element per decision, starting with the first decision.
If more decision outcomes are provided than decisions contained in the protocol,
additional decision outcomes are ignore.
If less decision outcomes are provided than decisions contained in the protocol,
all undefined decision outcomes will not be limited.

Example:
```
--protocol-path "decision1_outcome1,decision2_outcome1,decision3_outcome1"
```

To simulate multiple decision outcomes of a single decision,
allowed values have to be provided and seperated by a pipe symbol (`|`).
**Notice:** Depending on your shell, you might need to escape the pipe symbol or put the whole parameter in quotes.

Example:
```
--protocol-path "decision1_outcome1|decision1_outcome2,decision2_outcome1,decision3_outcome1"
```

To allow all possible outcomes for a single decision, you can use the wildcard symbol (`*`).

Example:
```
--protocol-path "decision1_outcome1|decision1_outcome2,*,decision3_outcome1"
```
