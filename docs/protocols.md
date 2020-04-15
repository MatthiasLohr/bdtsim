# Protocols

These protocols are currently supported (or planned to be supported) by BDTsim:

  * [SimplePayment](#simplepayment)
  * FairSwap ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/2))
  * Delgado-Segura ([planned](https://gitlab.com/MatthiasLohr/bdtsim/-/issues/1))


## SimplePayment

The SimplePayment protocol does nothing else than having the buyer paying the seller
(either direct or indirect using a smart contract as relay).
In case the buyer want's to "cheat", he just does not do the payment.

On the one hand, this protocol serves as a comparative evaluation to more complicated protocols, which, for example, have the goal of guaranteeing fairness.
On the other hand it serves as a simple protocol for internal tests of the framework.


### Example Protocol Execution

The following command executes the indirect variant of the SimplePayment protocol in the PyEVM environment:
```
bdtsim run -c 61 SimplePayment-indirect PyEVM
```
