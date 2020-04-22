# Protocols

These protocols are currently supported (or planned to be supported) by BDTsim:

  * [SimplePayment](#simplepayment)
  * FairSwap ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/2))
  * OptiSwap ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/5))
  * Delgado-Segura ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/1))


## SimplePayment

The SimplePayment protocol does nothing else than having the buyer paying the seller
(either direct or indirect using a smart contract as relay).
In case the buyer want's to "cheat", he just does not do the payment.

On the one hand, this protocol serves as a comparative evaluation to more complicated protocols, which, for example, have the goal of guaranteeing fairness.
On the other hand it serves as a simple protocol for internal tests of the framework.


### Example Protocol Execution

The following command executes the indirect variant of the SimplePayment protocol in the PyEVM environment,
using a smart contract for transferring the money to the seller:
```
bdtsim run -c 61 SimplePayment PyEVM
```


The following command executes the direct variant of the SimplePayment protocol in the PyEVM environment,
using a direct money transfer transaction without an intermediary smart contract.

## FairSwap

*(not implemented yet)*

FairSwap Paper:

> Dziembowski, S., Eckey, L., & Faust, S. (2018).
> Fairswap: How to fairly exchange digital goods.
> In Proceedings of the ACM Conference on Computer and Communications Security.
> [https://doi.org/10.1145/3243734.3243857](https://doi.org/10.1145/3243734.3243857)

Original example smart contract repository: [https://github.com/lEthDev/FairSwap](https://github.com/lEthDev/FairSwap).
Use kindly permitted by Lisa Eckey (16. April 2020).


## OptiSwap

*(not implemented yet)*

Original example smart contract repository: [https://github.com/CryBtoS/OptiSwap](https://github.com/CryBtoS/OptiSwap).
Use kindly permitted by Lisa Eckey (16. April 2020).


## Delgado-Segura

*(not implemented yet)*

Delgado-Segura Paper:

> Delgado-Segura, S., Pérez-Solà, C., Navarro-Arribas, G., & Herrera-Joancomartí, J. (2017).
> A fair protocol for data trading based on Bitcoin transactions.
> Future Generation Computer Systems.
> [https://doi.org/10.1016/j.future.2017.08.021](https://doi.org/10.1016/j.future.2017.08.021)
