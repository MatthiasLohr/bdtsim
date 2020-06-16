# Changelog

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
