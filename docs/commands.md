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


## list-protocols

`bdtsim list-protocols` prints a list of supported protocols to be simulated.
The printed values can be used as protocol argument for the [run](#run) command.

Please read the [protocols documentation](protocols.md) for more details.


## list-renderers

`bdtsim list-renderers` prints a list of supported renderers for printing/visualizing simulation results.
The listed renderer names can be used as renderer argument for the [render](#render) command.

Please read the [renderers documentation](renderer.md) for more details.


## render

`bdtsim render <renderer>` takes a simulation results and converts it into readable and interpretable output.
Use the [`list-renderers`](#list-renderers) command to get a list of available renderers.

The following parameters are available:

  * `-i <filename>`, `--input <filename>`: input file with simulation result, defaults to `-` (read from stdin)
  * `--input-compression <true/false>`: treat the input as gzip compressed data (after base64 decoding), defaults to `true`
  * `--input-b64encoding <true/false>`: strip base64 encoding (done before decompressing), defaults to `true`


## run

`bdtsim run <protocol> <environment>` simulates the behavior of a [protocol](protocols.md) in the given
[environment](environments.md).
The results are returned in form of a result file, which can be interpreted by the [`bdtsim render`](#render) command.
The result can either directly written to stdout or written to a result file using the `--output` parameter
(for more information, see parameter details below).

The following additional parameters are available:

  * `--account-file <filename>`: Specify account configuration file to be used.
    For details see [environment-info command](#environment-info)
  * `--protocol-path <protocol path>`: Limit protocol paths to be simulated
    ([more information/parameter format](commands_run_protocol_path.md)).
  * `--data-provider <data provider>`: set the [data provider](data_providers.md) to be used during the simulation
  * `--price <price>`: set the price for the asset to be traded
  * `-p <key> <value>`, `--protocol-parameter <key> <value>`: pass additional parameters to the protocol
  * `-e <key> <value>`, `--environment-parameter <key> <value>`: pass additional parameters to the environment
  * `-d <key> <value>`, `--data-provider-parameter <key> <value>`: pass additional parameters to the data provider
  * `-o <filename>`, `--output <filename>`: write output to the given file, defaults to `-`(write to stdout)
  * `--output-compression <true/false>`: do a gzip compression on the generated output (before base64 encoding), defaults to `true`
  * `--output-b64encoding <true/false>`: encode the output using the base64 standard (after compression), defaults to `true`
