# Environments

## PyEVM

The PyEVM environment offers a fast and cheap way of simulating locally without any connection to any
public blockchain instance.
The PyEVM environment provides a complete in-memory blockchain.
The PyEVM environment is based on the [Python Ethereum Virtual Machine (py-evm) project](https://github.com/ethereum/py-evm).

### Example Execution

```
bdtsim run -c 61 SimplePayment PyEVM
```

## Web3HTTP

bdtsim run SimplePayment-indirect Web3HTTP -e endpoint-uri https://ropsten.infura.io/v3/2dd8a2423914474ba5c2e8e72408773f -c 3 --tx-wait-timeout 300

## Web3Websocket

## Web3IPC
