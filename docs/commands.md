# Commands

The `bdtsim` command offers several sub-commands for carrying out simulations and working with the results.
Check `bdtsim -h` for a full list of supported commands and available parameters.

Below you can find more detailed information about available sub-commands:

## environment-info

`bdtsim environment-info <environment>` prints some information about the selected environment.

The following options are available:

  * `--account-file <filename>`: Specify account configuration file to be used.
    When not provided, wallets will be generated randomly and saved. File locations are

    * Linux: `$HOME/.config/bdtsim/accounts.yaml`
    * Windows: `%APPDATA%\bdtsim\accounts.yaml`

    File should look like:
```yaml
accounts:
  operator:
    name: Operator
    privateKey: <operators's private key>
  seller:
    name: Seller
    privateKey: <seller's private key>
  buyer:
    name: Buyer
    privateKey: <buyer's private key>
```
  * `-e <key> <value>`/`--environment-parameter <key> <value>`: Pass parameters (key/values pairs) to the selected environment.
    Please read the [environments documentation](environments.md) for a list of supported parameters, dependent on the selected environment.
    You can use `-e <key> <value>` multiple times to pass multiple key value pairs.

## list-data-providers

`bdtsim list-data-providers` prints a list of supported data providers to be used in the simulation.
The printed values can be used as data provider argument for the [run](#run) command.

Please read the [data providers documentation](data_providers.md) for more details.

## list-environments

`bdtsim list-environments` prints a list of supported environments in which simulations can be carried out.
The printed values can be used as environment argument for the [run](#run) command.

Please read the [environments documentation](environments.md) for more details.

## list-output-formats

`bdtsim list-output-formats` prints a list of supported output formats for the simulation results.
The printed values can be used as output format argument for the [run](#run) command.

Please read the [output formats documentation](output_formats.md) for more details.

## list-protocols

`bdtsim list-protocols` prints a list of supported protocols to be simulated.
The printed values can be used as protocol argument for the [run](#run) command.

Please read the [protocols documentation](protocols.md) for more details.

## run

`bdtsim run <protocol> <environment>` simulates the behavior of a [protocol](protocols.md) in the given
[environment](environments.md).

The following additional parameters are available:

  * `--account-file <filename>`: Specify account configuration file to be used.
    For details see [environment-info command](#environment-info)
  * `--data-provider DATA_PROVIDER`: set the [data provider](data_providers.md) to be used during the simulation
  * `-f OUTPUT_FORMAT`, `--output-format OUTPUT_FORMAT`: set the desired [output format](output_formats.md) for simulation results
  * `--price PRICE`: set the price for the asset to be traded
  * `-p KEY VALUE`, `--protocol-parameter KEY VALUE`: pass additional parameters to the protocol
  * `-e KEY VALUE`, `--environment-parameter KEY VALUE`: pass additional parameters to the environment
  * `-d KEY VALUE`, `--data-provider-parameter KEY VALUE`: pass additional parameters to the data provider
  * `-o KEY VALUE`, `--output-format-parameter KEY VALUE` pass additional parameters to the output format
