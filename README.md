# Blockchain Data Trading Simulator

## Usage

`bdtsim` offers several subcommands:
  * `bdtsim list-protocols` -- List all protocols supported for simulation
  * `bdtsim run` -- Run a simulation of the given protocol with the given environment.
    For more examples see [examples section](#examples)

Execute `bdtsim -h` to see a general help or `bdtsim <command> -h` for showing command specific options.


### Examples

  * Run TestProtocol with a Web3HTTPProvider using [Infura](https://infura.io/):
    ```
    bdtsim run TestProtocol Web3HTTP -e endpoint-uri https://ropsten.infura.io/v3/xxxxxxxxxxxxxxxxxxxxx
    ```

## License

This project is published under the Apache License, Version 2.0.
See [LICENSE.md](LICENSE.md) for more information.

Copyright (c) by Matthias Lohr <mail@mlohr.com>
