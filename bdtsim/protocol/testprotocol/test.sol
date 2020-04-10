pragma solidity ^0.6.1;

contract Test {
    function pay(address payable seller) payable public {
        seller.transfer(msg.value);
    }
}
