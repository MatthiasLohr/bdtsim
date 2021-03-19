# Changelog

## unreleased

  * Protocol: Delgado, Delgado-Reusable, Delgado-Library (#1)
  * Protocol: Support for SmartJudge (#20)
  * Renderer: Removed renderers `yaml`, `json` and `human-readable`
  * Renderer: Created new renderers `game-matrix` and `game-tree` (covers #33)
  * Renderer: Use scaling for all existing (`dot`, `game-matrix`, `game-tree`) renderers (#27)
  * Feature: Added event filtering support for environments
  * Feature: Added `--protocol-path` parameter for limiting protocol paths to be executed (#23)
  * Feature: Renderer: Add scaling support (#25)
  * Feature: Renderer: Graphviz Dot: Add option to show individual transactions in graph (#26)
  * Fix: Set default price to 1 ETH (#24)
  * Fix: Use gasPriceStrategy for determining gas price when available
  * Dependency Update: eth-tester to 0.5.0b3
  * Dependency Update: graphviz to 0.16
  * Dependency Update: hexbytes to 0.2.1
  * Dependency Update: Jinja2 to 2.11.3
  * Dependency Update: py-evm to 0.3.0a20
  * Dependency Update: py-solc-x to 1.1.0
  * Dependency Update: PyYAML to 5.4.1
  * Dependency Update: web3 to 5.17.0
  * Documentation: Updated documentation of Delgado protocol
  * New dependency: ecdsa 0.16.1
  * Other: Measure test coverage (#7)

## v1.1.1

  * Dependency Update: py-solc-x to 0.10.1
  * Achieved Raspberry Pi support (32/64 bit),
    for details see [https://gitlab.com/MatthiasLohr/bdtsim/-/wikis/Raspberry-Pi](https://gitlab.com/MatthiasLohr/bdtsim/-/wikis/Raspberry-Pi)

## v1.1.0

  * Dependency Update: web3py 5.11.1
  * Dependency Update: eth-tester 0.5.0b1
  * Dependency Update: py-evm 0.3.0a17
  * Protocol: FairSwap with Reusable Smart Contract (#18)
  * Feature: `environment-info` prints account balances (#21)
  * Feature: Added parameter for `environment-info` and `run` to define accounts to be used (#22)
  * Fix: Complain about unrecognized parameters
  * Fix: When `-o view True` is given without an output filename use temporary file
  * Fix: Allow slices-count >= 256 in FairSwap contract


## v1.0.0

  * Docker image creation
  * Support for FairSwap protocol (#2)
  * Support for Goerli Testnet (#10)
  * Added sub-command `environment-info`
  * Enabled DataProvider support
    * added `list-data-providers` command
  * Improved output format support
    * added `list-output-formats` command
    * support for Graphviz dot output (#12)
    * support for human readable output (#14)
  * Value Transfer Tracking (#15)


## v0.1.2

  * Added support for Python 3.8


## v0.1.1

  * Fix: Include Solidity Smart Contract files in Python Wheel
  * Fix: Absolute link in README.md


## v0.1.0

  * First release of BDTsim simulation tool
  * First supported protocol (also used for internal teste) with two variants
    * [SimplePayment](https://gitlab.mlohr.com/bdtsim/protocols/#simplepayment) (direct and indirect payment)
  * Supported environments:
    * [PyEVM](https://gitlab.mlohr.com/bdtsim/environments/#pyevm)
    * [Web3HTTP](https://gitlab.mlohr.com/bdtsim/environments/#web3http)
    * [Web3Websocket](https://gitlab.mlohr.com/bdtsim/environments/#web3socket)
    * [Web3IPC](https://gitlab.mlohr.com/bdtsim/environments/#web3ipc)
