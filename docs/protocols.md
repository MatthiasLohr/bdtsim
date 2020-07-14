# Protocols

These protocols are currently supported (or planned to be supported) by BDTsim:

  * [SimplePayment](#simplepayment)
  * [FairSwap](#fairswap)
  * OptiSwap ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/5))
  * Delgado-Segura ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/1))


## Supported Protocols

### SimplePayment

The SimplePayment protocol does nothing else than having the buyer paying the seller
(either direct or indirect using a smart contract as relay).
In case the buyer want's to "cheat", he just does not do the payment.

On the one hand, this protocol serves as a comparative evaluation to more complicated protocols, which, for example, have the goal of guaranteeing fairness.
On the other hand it serves as a simple protocol for internal tests of the framework.


#### Example Protocol Execution

The following command executes the indirect variant of the SimplePayment protocol in the PyEVM environment,
using a smart contract for transferring the money to the seller:
```
bdtsim run SimplePayment PyEVM
```

The following command executes the direct variant of the SimplePayment protocol in the PyEVM environment,
using a direct money transfer transaction without an intermediary smart contract:
```
bdtsim run SimplePayment-direct PyEVM
```

### FairSwap

The FairSwap protocol was presented in the following research paper:

> Dziembowski, S., Eckey, L., & Faust, S. (2018).
> Fairswap: How to fairly exchange digital goods.
> In Proceedings of the ACM Conference on Computer and Communications Security.
> [https://doi.org/10.1145/3243734.3243857](https://doi.org/10.1145/3243734.3243857)

It is available within BDTsim with the name `FairSwap`.
There is also a protocol `FairSwap-Reusable`, which deploys a reusable variant of the FairSwap smart contract.

Original example smart contract repository: [https://github.com/lEthDev/FairSwap](https://github.com/lEthDev/FairSwap).
Use kindly permitted by Lisa Eckey (16. April 2020).

Protocol Assumptions:

  * Both seller and buyer know the plain data's Merkle Tree root hash before the exchange (simulation process) is started

Buyer Complaint Types:

  * **Complain About Root**, raised when 
    * wrong decryption key
    * wrong plain file encrypted
  * **Complain About Node**, raised when
    * intentional modification of a hash value in a non-leaf node
  * **Complain About Leaf**, raised when
    * intentional modification of leaf value

#### Protocol Parameters

  * `slices-count`: Number of slices in which the data is to be split
  * `timeout`: Timeout in seconds before refund can be used

#### Example Protocol Execution

```
bdtsim -l DEBUG run FairSwap PyEVM -p slices-count 8
```

### OptiSwap

*(not implemented yet)*

Original example smart contract repository: [https://github.com/CryBtoS/OptiSwap](https://github.com/CryBtoS/OptiSwap).
Use kindly permitted by Lisa Eckey (16. April 2020).


### Delgado-Segura

*(not implemented yet)*

Delgado-Segura Paper:

> Delgado-Segura, S., Pérez-Solà, C., Navarro-Arribas, G., & Herrera-Joancomartí, J. (2017).
> A fair protocol for data trading based on Bitcoin transactions.
> Future Generation Computer Systems.
> [https://doi.org/10.1016/j.future.2017.08.021](https://doi.org/10.1016/j.future.2017.08.021)
