# Commands

The `bdtsim` command offers several sub-commands for carrying out simulations and working with the results.
Check `bdtsim -h` for a full list of supported commands and available parameters.

The following sections provide more detailed information about available sub-commands:


## list-protocols

`bdtsim list-protocols` prints a list of supported protocols to be simulated.
The printed values can be used as protocol argument for the [run](#run) command.


## list-environments

`bdtsim list-environments` prints a list of supported environments in which simulations can be carried out.
The printed values can be used as environment argument for the [run](#run) command.

## run

`bdtsim run <protocol> <environments>` simulates the behavior of protocol `<protocol>` in the environment `<environment>`.
