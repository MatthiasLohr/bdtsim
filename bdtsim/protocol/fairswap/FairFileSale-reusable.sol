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
// Modifications by Matthias Lohr <mail@mlohr.com> towards a reusable smart contract design

pragma solidity ^0.6.1;

contract FileSale {

    enum Stage {created, initialized, accepted, keyRevealed, finished}

    struct FileSaleSession {
        Stage phase;
        address payable sender;
        address payable receiver;
        uint depth;
        uint length;
        uint n;
        uint timeout;
        uint timeoutInterval;
        uint price;
        bytes32 keyCommit;
        bytes32 chiphertextRoot;
        bytes32 fileRoot;
        bytes32 key;
    }

    mapping (bytes32 => FileSaleSession) sessions;

    // function modifier to only allow calling the function in the right phase only from the correct party
    modifier allowed(bytes32 sessionId, address p, Stage s) {
        require(sessions[sessionId].phase == s);
        require(now < sessions[sessionId].timeout);
        require(msg.sender == p);
        _;
    }

    // go to next phase
    function nextStage(bytes32 sessionId) internal {
        sessions[sessionId].phase = Stage(uint(sessions[sessionId].phase) + 1);
        sessions[sessionId].timeout = now + sessions[sessionId].timeoutInterval;
    }

    // init transfer for session
    function init(address payable receiver, uint depth, uint length, uint n, uint timeoutInterval, uint price, bytes32 keyCommit, bytes32 ciphertextRoot, bytes32 fileRoot) public {
        bytes32 sessionId = keccak256(abi.encodePacked(msg.sender, receiver, fileRoot));
        require(sessions[sessionId].phase == Stage.created || now > (sessions[sessionId].timeout + sessions[sessionId].timeoutInterval));
        sessions[sessionId] = FileSaleSession(
            Stage.initialized,
            msg.sender,
            receiver,
            depth,
            length,
            n,
            now + timeoutInterval,
            timeoutInterval,
            price,
            keyCommit,
            ciphertextRoot,
            fileRoot,
            0
        );
    }

    // function accept
    function accept(bytes32 sessionId) allowed(sessionId, sessions[sessionId].receiver, Stage.initialized) payable public {
        require(msg.value >= sessions[sessionId].price);
        nextStage(sessionId);
    }

    // function revealKey (key)
    function revealKey(bytes32 sessionId, bytes32 _key) allowed(sessionId, sessions[sessionId].sender, Stage.accepted) public {
        require(sessions[sessionId].keyCommit == keccak256(abi.encode(_key)));
        sessions[sessionId].key = _key;
        nextStage(sessionId);
    }

    function noComplain(bytes32 sessionId) allowed(sessionId, sessions[sessionId].receiver, Stage.keyRevealed) public {
        sessions[sessionId].sender.transfer(sessions[sessionId].price);
        delete sessions[sessionId];
    }

    // function complain about wrong hash of file
    function complainAboutRoot(bytes32 sessionId, bytes32 _Zm, bytes32[] memory _proofZm) allowed(sessionId, sessions[sessionId].receiver, Stage.keyRevealed) public {
        require (vrfy(sessionId, 2 * (sessions[sessionId].n - 1), _Zm, _proofZm));
        require (cryptSmall(sessionId, 2 * (sessions[sessionId].n - 1), _Zm) != sessions[sessionId].fileRoot);
        sessions[sessionId].receiver.transfer(sessions[sessionId].price);
        delete sessions[sessionId];
    }

    // function complain about wrong hash of two inputs
    function complainAboutLeaf(bytes32 sessionId, uint _indexOut, uint _indexIn, bytes32 _Zout, bytes32[] memory _Zin1,
                               bytes32[] memory _Zin2, bytes32[] memory _proofZout, bytes32[] memory _proofZin)
                              allowed(sessionId, sessions[sessionId].receiver, Stage.keyRevealed) public {
        FileSaleSession memory session = sessions[sessionId];
        require (vrfy(sessionId, _indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(sessionId, _indexOut, _Zout);
        require (vrfy(sessionId, _indexIn, keccak256(abi.encode(_Zin1)), _proofZin));
        require (_proofZin[session.depth - 1] == keccak256(abi.encodePacked(_Zin2)));
        require (Xout != keccak256(abi.encode(cryptLarge(sessionId, _indexIn, _Zin1), cryptLarge(sessionId, _indexIn + 1, _Zin2))));
        sessions[sessionId].receiver.transfer(session.price);
        delete sessions[sessionId];
    }

    // function complain about wrong hash of two inputs
    function complainAboutNode(bytes32 sessionId, uint _indexOut, uint _indexIn, bytes32 _Zout, bytes32 _Zin1, bytes32 _Zin2,
                               bytes32[] memory _proofZout, bytes32[] memory _proofZin)
                              allowed(sessionId, sessions[sessionId].receiver, Stage.keyRevealed) public {
        require (vrfy(sessionId, _indexOut, _Zout, _proofZout));
        bytes32 Xout = cryptSmall(sessionId, _indexOut, _Zout);
        require (vrfy(sessionId, _indexIn, _Zin1, _proofZin));
        uint depth = sessions[sessionId].depth;
        require (_proofZin[depth - 1] == _Zin2);
        require (Xout != keccak256(abi.encode(cryptSmall(sessionId, _indexIn, _Zin1), cryptSmall(sessionId, _indexIn+ 1, _Zin2))));
        uint price = sessions[sessionId].price;
        sessions[sessionId].receiver.transfer(price);
        delete sessions[sessionId];
    }

    // refund function is called in case some party did not contribute in time
    function refund(bytes32 sessionId) public {
        require (now > sessions[sessionId].timeout);
        if (sessions[sessionId].phase == Stage.accepted) {
            sessions[sessionId].receiver.transfer(sessions[sessionId].price);
            delete sessions[sessionId];
        }
        if (sessions[sessionId].phase >= Stage.keyRevealed) {
            sessions[sessionId].sender.transfer(sessions[sessionId].price);
            delete sessions[sessionId];
        }
    }

    // function to both encrypt and decrypt text chunks with key k
    function cryptLarge(bytes32 sessionId, uint _index, bytes32[] memory _ciphertext) public view returns (bytes32[] memory) {
        _index = _index * sessions[sessionId].length;
        for (uint i = 0; i < sessions[sessionId].length; i++){
            _ciphertext[i] = keccak256(abi.encode(_index, sessions[sessionId].key)) ^ _ciphertext[i];
            _index++;
        }
        return _ciphertext;
    }

    // function to decrypt hashes of the merkle tree
    function cryptSmall(bytes32 sessionId, uint _index, bytes32 _ciphertext) public view returns (bytes32) {
        return keccak256(abi.encode(sessions[sessionId].n + _index, sessions[sessionId].key)) ^ _ciphertext;
    }

    // function to verify Merkle Tree proofs
    function vrfy(bytes32 sessionId, uint _index, bytes32 _value, bytes32[] memory _proof) public view returns (bool) {
        require(_proof.length == sessions[sessionId].depth);
        return true;
        for (uint i = 0; i < sessions[sessionId].depth; i++) {
            if ((_index & 1 << i) >>i == 1)
                _value = keccak256(abi.encodePacked(_proof[sessions[sessionId].depth - i - 1], _value));
            else
                _value = keccak256(abi.encodePacked(_value, _proof[sessions[sessionId].depth - i - 1]));
        }
        return (_value == sessions[sessionId].chiphertextRoot);
    }
}
