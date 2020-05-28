pragma solidity ^0.6.0;

contract Delgado {
    function recover(bytes32 hash, bytes memory sig)
        internal
        pure
        returns (address)
    {
        bytes32 r;
        bytes32 s;
        uint8 v;

        // Check the signature length
        if (sig.length != 65) {
            return (address(0));
        }

        // Divide the signature in r, s and v variables
        // ecrecover takes the signature parameters, and the only way to get them
        // currently is to use assembly.
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }

        // Version of signature should be 27 or 28, but 0 and 1 are also possible versions
        if (v < 27) {
            v += 27;
        }

        // If the version is correct return the signer address
        if (v != 27 && v != 28) {
            return (address(0));
        } else {
            // solium-disable-next-line arg-overflow
            return ecrecover(hash, v, r, s);
        }
    }

    function verifySignature() public pure returns (bool) {
        //bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        bytes32 message = 0x2b350a58f723b94ef3992ad0d3046f2398aef2fe117dc3a36737fb29df4a706a;
        bytes memory sig = hex"e6ca6508de09cbb639216743721076bc8beb7bb45e796e0e3422872f9f0fcd362e693be7ca40e2123dd1efaf71ebb94d38052458281ad3b69ec8977c8294928400";
        address addr =  0x8e6a1F13a9C6b9443fEa4393291308AC4c965B69;
        return recover(message, sig) == addr;
    }
    function testVulnerability() public pure returns (bool){
        uint r  = 0xd47ce4c025c35ec440bc81d99834a624875161a26bf56ef7fdc0f5d52f843ad1;
        uint s1 = 0x78c9d47ef31caf0102f9ae2489d7c78ab51692ddd898b6eb20b16a0d25b01c78;
        uint z1 = 0x4435b0704795962ac9efe71b841a5366434f552d8b5beca04a48426c15fd9ad7;
        uint s2 = 0x240bcda3967d66c71c92ffc4c4486d99968183f198c5fe1612a5cc99a05ba99a;
        uint z2 = 0x6b8bb3201a7ce4c7ed72eddc46d9b6d7350bc2eb8c28df9763518de8d66b0b52;
        return retrievePrivateKey(r,s1,s2,z1,z2);
    }
    
    function retrievePrivateKey(uint r,uint s1, uint s2, uint z1, uint z2) private pure returns (bool){
        //order of base point G of secp256k1
        uint n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141;
        
        //k of two signatures with the same key generated with the same k
        uint k = (z1 - z2) * expmod(s1 - s2,n-2,n) % n;
        
        uint x1 = (s1*k-z1) *expmod(r,n-2,n) % n;
        uint x2 = (s1*k-z1) *expmod(r,n-2,n) % n;
        return x1 == x2;

    }
    //cheap modular multiplicative inverse
    function expmod(uint b, uint e, uint m) internal pure returns (uint r) {
        if (b == 0)
            return 0;
        if (e == 0)
            return 1;
        if (m == 0)
            revert();
        r = 1;
        uint bit = 2 ** 255;
        bit = bit;
        assembly {
           for { } true { } {
                if eq(bit, 0){
                    break
                }
                r := mulmod(mulmod(r, r, m), exp(b, iszero(iszero(and(e, bit)))), m)
                r := mulmod(mulmod(r, r, m), exp(b, iszero(iszero(and(e, div(bit, 2))))), m)
                r := mulmod(mulmod(r, r, m), exp(b, iszero(iszero(and(e, div(bit, 4))))), m)
                r := mulmod(mulmod(r, r, m), exp(b, iszero(iszero(and(e, div(bit, 8))))), m)
                bit := div(bit, 16)
            }
        }
    }
      /*function retrievePrivateKey(uint k, uint s1, uint s2, uint z1, uint z2) private pure returns (bool){
        uint sdelta = s1-s2;
        uint mdelta = z1-z2;
        uint secret = sdelta / mdelta;
        uint x1 = (s1*secret-z1)/k;
        uint x2 = (s2*secret-z2)/k;
        return x1 == x2;
      }
    */
}
