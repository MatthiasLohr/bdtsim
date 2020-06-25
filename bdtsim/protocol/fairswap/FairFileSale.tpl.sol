// This file is part of the Blockchain Data Trading Simulator
//    https://gitlab.com/MatthiasLohr/bdtsim
//
// Copyright 2020 Matthias Lohr <mail@mlohr.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This file originates from https://github.com/lEthDev/FairSwap
// Original authors: Stefan Dziembowski, Lisa Eckey, Sebastian Faust
//
// Modifications by Matthias Lohr <mail@mlohr.com> to enable practical usability and improve readability

pragma solidity ^0.6.1;

contract FileSale {

    uint constant depth = {{ merkle_tree_depth }};
    uint constant length = {{ slice_length }};
    uint constant n = {{ slices_count }};

    enum stage {created, initialized, accepted, keyRevealed, finished}
    stage public phase = stage.created;
    uint public timeout;

    address payable public sender;
    address payable public receiver = {{ receiver }};
    uint price = {{ price }};

    bytes32 public keyCommit = {{ key_commitment }};
    bytes32 public chiphertextRoot = {{ ciphertext_root_hash }};
    bytes32 public fileRoot = {{ file_root_hash }};

    bytes32 public key;

    // function modifier to only allow calling the function in the right phase only from the correct party
    modifier allowed(address p, stage s) {
        require(phase == s);
        require(now < timeout);
        require(msg.sender == p);
        _;
    }

    // go to next phase
    function nextStage() internal {
        phase = stage(uint(phase) + 1);
        timeout = now + {{ timeout }} seconds;
    }

    // constructor is initialize function
    constructor() public {
        sender = msg.sender;
        nextStage();
    }

    // function accept
    function accept() allowed(receiver, stage.initialized) payable public {
        require (msg.value >= price);
        nextStage();
    }

    // function revealKey (key)
    function revealKey(bytes32 _key) allowed(sender, stage.accepted) public {
        require(keyCommit == keccak256(abi.encode(_key)));
        key = _key;
        nextStage();
    }

    function noComplain() allowed(receiver, stage.keyRevealed) public {
        selfdestruct(sender);
    }

    // function complain about wrong hash of file
    function complainAboutRoot(bytes32 _Zm, bytes32[depth] memory _proofZm) allowed(receiver, stage.keyRevealed) public {
        require (vrfy(2 * (n - 1), _Zm, _proofZm));
        require (cryptSmall(2 * (n - 1), _Zm) != fileRoot);
        selfdestruct(receiver);
    }

    // function complain about wrong hash of two inputs
    function complainAboutLeaf(uint _indexOut, uint _indexIn, bytes32 _Zout, bytes32[length] memory _Zin1,
                               bytes32[length] memory _Zin2, bytes32[depth] memory _proofZout, bytes32[depth] memory _proofZin)
                              allowed(receiver, stage.keyRevealed) public {
        require (vrfy(_indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(_indexOut, _Zout);
        require (vrfy(_indexIn, keccak256(abi.encode(_Zin1)), _proofZin));
        require (_proofZin[depth - 1] == keccak256(abi.encode(_Zin2)));
        require (Xout != keccak256(abi.encode(cryptLarge(_indexIn, _Zin1), cryptLarge(_indexIn + 1, _Zin2))));
        selfdestruct(receiver);
    }

    // function complain about wrong hash of two inputs
    function complainAboutNode(uint _indexOut, uint _indexIn, bytes32 _Zout, bytes32 _Zin1, bytes32 _Zin2,
                               bytes32[depth] memory _proofZout, bytes32[depth] memory _proofZin)
                              allowed(receiver, stage.keyRevealed) public {
        require (vrfy(_indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(_indexOut, _Zout);
        require (vrfy(_indexIn, _Zin1, _proofZin));
        require (_proofZin[depth - 1] == _Zin2);
        require (Xout != keccak256(abi.encode(cryptSmall(_indexIn, _Zin1), cryptSmall(_indexIn+ 1, _Zin2))));
        selfdestruct(receiver);
    }

    // refund function is called in case some party did not contribute in time
    function refund() public {
        require (now > timeout);
        if (phase == stage.accepted) selfdestruct (receiver);
        if (phase >= stage.keyRevealed) selfdestruct (sender);
    }

    // function to both encrypt and decrypt text chunks with key k
    function cryptLarge(uint _index, bytes32[length] memory _ciphertext) public view returns (bytes32[length] memory) {
        _index = _index * length;
        for (uint i = 0; i < length; i++){
            _ciphertext[i] = keccak256(abi.encode(_index, key)) ^ _ciphertext[i];
            _index++;
        }
        return _ciphertext;
    }

    // function to decrypt hashes of the merkle tree
    function cryptSmall(uint _index, bytes32 _ciphertext) public view returns (bytes32) {
        return keccak256(abi.encode(n + _index, key)) ^ _ciphertext;
    }

    // function to verify Merkle Tree proofs
    function vrfy(uint _index, bytes32 _value, bytes32[depth] memory _proof) public view returns (bool) {
        for (uint i = 0; i < depth; i++) {
            if ((_index & 1 << i) >>i == 1)
                _value = keccak256(abi.encodePacked(_proof[depth - i - 1], _value));
            else
                _value = keccak256(abi.encodePacked(_value, _proof[depth - i - 1]));
        }
        return (_value == chiphertextRoot);
    }
}
