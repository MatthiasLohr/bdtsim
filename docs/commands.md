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

The following options are available:

  * `-c <chain id>`/`--chain-id <chain id>`: Set the Chain Id for blockchain transactions. Depends on the Ethereum network you want to use.
  * `-o <format>`/`--output-format <format>`: Output format for the simulation results.
    Allowed values are `human-readable`, `json` and `yaml`.
  * `--gas-price <gas price>`: Define the gas price for the transactions. By default, BDTsim tries to fetch the gas price from the
    network, using Web3's [Gas Price API](https://web3py.readthedocs.io/en/stable/gas_price.html)
  * `--gas-price-factor <gas price factor>`: Multiply the gas price specified with `--gas-price` or fetched from the network with this factor.
  * `--tx-wait-timeout <timeout>`: Define the timeout for waiting for a transaction to get added to the network. Default ist 120 seconds.
  * `-p <key> <value>`/`--protocol-parameter <key> <value>`: Pass parameters (key/value pairs to the selected protocol.
    Please read the [Protocols documentation](protocols.md) for a list of supported parameters, dependent on the selected protocol.
    You can use this parameters multiple times.
  * `-e <key> <value>`/`--environment-parameter <key> <value>`: Pass parameters (key/values pairs) to the selected environment.
    Please read the [Environment documentation](environments.md) for a list of supported parameters, dependent on the selected environment.
    You can use this parameters multiple times.
