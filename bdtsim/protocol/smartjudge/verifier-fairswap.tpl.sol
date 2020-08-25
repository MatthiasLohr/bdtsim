pragma solidity ^0.4.26;

import {Verifier, Mediator} from "mediator.sol";

contract fileSale {

    // This can be set dynamically for each trade. In that case, these parameters have to be included
    // in the initial agreement, revealed in verify_initial_agreement() and stored in the Verification struct.
    // In order to be able to set a worst-case execution cost for the verifier, this size has to be bound though.
    uint constant depth = {{ merkle_tree_depth }};
    uint constant length = {{ slice_length }}; // length in bytes32
    uint constant n = {{ slices_count }};

    enum stage {pre, created, initialized}
    struct Verification{
        stage phase;
        uint timeout;
        uint256 id;
        address sender;
        address receiver;
        uint price; // in wei
        bytes32 bobfunds;
        bytes32 initial;
        bytes32 keyCommit ;
        bytes32 ciphertextRoot ;
        bytes32 fileRoot ;
        bytes32 key;
    }

    address managmentAddress;
    mapping(uint32 => Verification) verifier;

    bytes32 public keystored;
    // function modifier to only allow calling the function in the right phase only from the correct party
    modifier allowed(uint32 id, address p, stage s ) {
        var v  = verifier[id];
        require(v.phase == s);
        require(now < v.timeout);
        require(msg.sender == p);
        _;
    }
    event address_event(address addressStuff);
    event result(stage);
    event debug( int value);
    event b(bytes32 value);


    constructor(address _managmentAddress) public {
      managmentAddress = _managmentAddress;
      emit address_event(managmentAddress); 
    }

    function publish_result(uint32 _id, address _honest_party){
        Mediator managmentContract = Mediator(managmentAddress);
        managmentContract.verifier_callback(_id, _honest_party);
    }

    // go to next phase
    function nextStage(uint32 id) internal {
        var v = verifier[id];
        v.phase = stage(uint(v.phase) + 1);
        v.timeout = now + 10 minutes;
    }
    
    function construct_hash(bytes32 __key, bytes32 __cipher, bytes32 __file) returns (bytes32){
        return keccak256(__key,__cipher,__file);
    }

    function start_verification(address alice, address bob, uint32 id, bytes32 initial_agreement, bytes32 witness){
        require(msg.sender == managmentAddress);
        var v = verifier[id];
        require(v.phase == stage.pre);
        v.sender = bob;
        v.receiver = alice;
        v.key = witness;
        v.initial = initial_agreement;
        nextStage(id);
    }

    // constructor is initialize function
    function verify_initial_agreement(uint32 id, bytes32 _ciphertextRoot, bytes32 _fileRoot) public {
        var v = verifier[id];
        require(v.phase == stage.created);
        require(msg.sender == v.sender);
        v.ciphertextRoot = _ciphertextRoot;
        v.fileRoot = _fileRoot;
        if (sha3(abi.encodePacked(v.key,v.ciphertextRoot,v.fileRoot)) == v.initial){
            nextStage(id);
        }
        else{
            v.phase = stage.pre;
            publish_result(id, v.receiver);
        }
    }

    // function complain about wrong hash of file
    function complainAboutRoot (uint32 id, bytes32 _Zm, bytes32[depth] _proofZm)  public {
        var v = verifier[id];
        require( v.phase == stage.initialized );
        require (vrfy(id,2*(n-1), _Zm, _proofZm));
        if (cryptSmall(id, 2*(n-1), _Zm) != v.fileRoot){
            publish_result(id, v.receiver);
            v.phase = stage.pre;
        }
    }


    // function complain about wrong hash of two inputs
    function complainAboutLeaf (uint32 id, uint _indexOut, uint _indexIn,
        bytes32 _Zout, bytes32[length] _Zin1, bytes32[length] _Zin2, bytes32[depth] _proofZout,
        bytes32[depth] _proofZin) public {
        var v = verifier[id];
        require(v.receiver == msg.sender);
        require(stage.initialized == v.phase);
        
        require(vrfy(id, _indexOut, _Zout, _proofZout));
        
        bytes32 Xout = cryptSmall(id, _indexOut, _Zout);

        require( vrfy(id, _indexIn, keccak256(_Zin1), _proofZin));
        
        require (_proofZin[depth - 1] == keccak256(_Zin2));

        if (Xout != keccak256(cryptLarge(id, _indexIn, _Zin1), cryptLarge(id, _indexIn+1, _Zin2))) {
            v.phase = stage.pre;
            publish_result(id, v.receiver);
            v.phase = stage.pre;
        }
    }


    // function complain about wrong hash of two inputs
    function complainAboutNode (uint32 id, uint _indexOut, uint _indexIn,
        bytes32 _Zout, bytes32 _Zin1, bytes32 _Zin2, bytes32[depth] _proofZout,
        bytes32[depth] _proofZin) public {
        
        var v = verifier[id];
        
        require( vrfy(id, _indexOut, _Zout, _proofZout));

        require( vrfy(id, _indexIn, _Zin1, _proofZin));
        require(_proofZin[depth - 1] == _Zin2);
        
        bytes32 Xout = cryptSmall(id, _indexOut, _Zout);

        if (Xout != keccak256(cryptSmall(id, _indexIn, _Zin1), cryptSmall(id, _indexIn+1, _Zin2))) {
            publish_result(id, v.receiver);
            v.phase = stage.pre;
        }
    }


    // refund function is called in case some party did not contribute in time
    function refund (uint32 id) public {
        var v = verifier[id];
        require (now > v.timeout);
        if (v.phase == stage.created) {

            publish_result(id, v.receiver);
            v.phase = stage.pre;
        }
        else if (v.phase >= stage.initialized) {

            publish_result(id, v.sender);
            v.phase = stage.pre;
        }
    }



    // function to both encrypt and decrypt text chunks with key k
    function cryptLarge (uint32 id, uint _index, bytes32[length] _ciphertext) public view returns (bytes32[length]){
        var v = verifier[id];
        _index = _index*length;
        for (uint i = 0; i < length; i++){
            _ciphertext[i] = keccak256(_index, v.key) ^ _ciphertext[i];
            _index++;
        }
        return _ciphertext;
    }

    // function to decrypt hashes of the merkle tree
    function cryptSmall (uint32 id, uint _index, bytes32 _ciphertext) public view returns (bytes32){
        var v = verifier[id];
        return keccak256(_index, v.key) ^ _ciphertext;
    }


    // function to verify Merkle Tree proofs
    function vrfy(uint32 id, uint _index, bytes32 _value, bytes32[depth] _proof) public view returns (bool){
        var v = verifier[id];

        for (uint i = 0; i < depth; i++){
            if ((_index & 1<<i)>>i == 1){
                _value = keccak256(_proof[depth - i - 1], _value);
            } else {
                _value = keccak256(_value, _proof[depth - i - 1]);
            }
        }
        return (_value == v.ciphertextRoot);
    }

}
