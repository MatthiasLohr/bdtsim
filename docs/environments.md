# Environments

## PyEVM

The PyEVM environment offers a fast and cheap way of simulating locally without any connection to any
public blockchain instance.
The PyEVM environment provides a complete in-memory blockchain.
The PyEVM environment is based on the [Python Ethereum Virtual Machine (py-evm) project](https://github.com/ethereum/py-evm).


### Environment Parameters

No special environment parameters available.


### Example Usage

```
bdtsim run -c 61 SimplePayment PyEVM
```


## Web3HTTP

The Web3HTTP environment allows to use an existing blockchain network where you have access to an HTTP endpoint
(e.g. using [Infura](https://infura.io/)).


### Environment Parameters

  * `endpoint-uri`: HTTP Endpoint URI (e.g. https://ropsten.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
  
### Example Usage

```
bdtsim run -c 3 SimplePayment Web3HTTP -e endpoint-uri https://ropsten.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```


## Web3Websocket

This environment works analogous to the [Web3HTTP](#web3http) environment, including the environment parameters.
Use this environment if you want to use WebSockets instead of a HTTP endpoint.


## Web3IPC

This environment allows to connect to a unix domain socket on your local machine.


### Environment Parameters

  * `ipc_path`: Path to your unix domain socket of a locally available network client.


### Example Usage

```
bdtsim run SimplePayment Web3IPC -e ipc_path /var/lib/geth/geth.ipc
```
