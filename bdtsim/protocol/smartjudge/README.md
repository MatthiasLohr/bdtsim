## SmartJudge

The directory `COMSYS-smartjudge` contains the original SmartJudge smart contract source code
as it was published by the authors of the original SmartJudge paper.

> Eric Wagner, Achim Völker, Frederik Fuhrmann, Roman Matzutt and Klaus Wehrle.
> Dispute Resolution for Smart-contract bases Two-Party Protocols
> IEEE International Conference on Blockchain and Cryptocurrency 2019 (ICBC 2019)

The original repository is available at https://github.com/COMSYS/smartjudge.
Source code is under MIT license.
Last update at 08. July 2020.


### SmartJudge with FairSwap

The directory `COMSYS-smartjudge-fairswap` contains the original SmartJudge smart contract source code
combined with the FairSwap protocol.
Use kindly permitted by Eric Wagner (10. July 2020).

#### Known Issues

The contract implementation has the following known issues:

  * `conditions_hash = keccak(key, z_hash, pt_hash)` has to be calculated by the seller since it contains the plain `key` value.
    Can be fixed without conceptual change by using `conditions_hash = keccak(keccak(key), z_hash, pt_hash)` instead.
  * SmartJudge would accept revealing the key using the `reveal` method. However, the provided FairSwap verifier only implements off-chain key release.