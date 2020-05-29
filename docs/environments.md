# Environments

The environment is the actual blockchain instance in which the simulation is carried out.
This enabled to use a virtual, private, or public blockchain based on Ethereum.

## General Environment Parameters

These environment parameters are supported by any environment:

  * `chain-id`: can be used to overwrite the auto-detected chain id detected by BDTsim
  * `gas-price`: can be used to manually set a gas price for the transaction.
    By default, BDTsim uses [Web3's `fast_gas_price_strategy`](https://web3py.readthedocs.io/en/stable/gas_price.html#module-web3.gas_strategies.rpc).

## Supported Environments

### PyEVM

The PyEVM environment offers a fast and cheap way of simulating locally without any connection to any
public blockchain instance.
The PyEVM environment provides a complete in-memory blockchain.
The PyEVM environment is based on the [Python Ethereum Virtual Machine (py-evm) project](https://github.com/ethereum/py-evm).

#### Environment Parameters

No special environment parameters available.

#### Example Usage

```
bdtsim run -c 61 SimplePayment PyEVM
```

### Web3HTTP

The Web3HTTP environment allows to use an existing blockchain network where you have access to an HTTP endpoint
(e.g. using [Infura](https://infura.io/)).


#### Environment Parameters

  * `endpoint-uri`: HTTP Endpoint URI (e.g. https://ropsten.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
  * `inject-poa-middleware`: When connecting to an POA network, you have to use this middleware. Value should be `True`.
  
#### Example Usage

##### Ethereum Mainnet

```
bdtsim run SimplePayment Web3HTTP -e endpoint-uri https://mainnet.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

##### Ropsten Testnet

```
bdtsim run SimplePayment Web3HTTP -e endpoint-uri https://ropsten.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

##### Goerli Testnet

```
bdtsim run SimplePayment Web3HTTP -e endpoint-uri https://rpc.slock.it/goerli -e inject-poa-middleware True
```

### Web3Websocket

This environment works analogous to the [Web3HTTP](#web3http) environment, including the environment parameters.
Use this environment if you want to use WebSockets instead of a HTTP endpoint.


### Web3IPC

This environment allows to connect to a unix domain socket on your local machine.


#### Environment Parameters

  * `ipc-path`: Path to your unix domain socket of a locally available network client.
  * `inject-poa-middleware`: When connecting to an POA network, you have to use this middleware. Value should be `True`.


#### Example Usage

```
bdtsim run SimplePayment Web3IPC -e ipc-path /var/lib/geth/geth.ipc
```
