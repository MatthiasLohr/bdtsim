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

pragma solidity >=0.6.1;

abstract contract EllipticCurve {
   function ecMul(uint256 _k,uint256 _x,uint256 _y,uint256 _aa,uint256 _pp) public pure virtual returns(uint256, uint256);
}


contract Delgado {

  uint256 public constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
  uint256 public constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
  uint256 public constant AA = 0;
  uint256 public constant BB = 7;
  uint256 public constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;
  uint256 _pubX;
  uint256 _pubY;
  uint price = {{ price }};
  uint public timeout;
  uint public time = {{ time }} seconds;
  enum stage {created, initialized, finished}
  stage public phase = stage.created;
  address payable buyer;
  address payable seller;
  EllipticCurve ec;
  address lib = {{ lib }};

  modifier allowed(address p, stage s) {
        require(phase == s,"phase wrong");
        require(now < timeout,"timeout wrong");
        require(msg.sender == p,"sender wrong");
        _;
    }

    constructor() public {
        buyer = msg.sender;
        timeout = now + time;
        ec = EllipticCurve(lib);
    }
    
function BuyerInitTrade(uint256 pubX,uint256 pubY, address payable s) allowed(buyer,stage.created) payable public{
    require(msg.value >= price,"price wrong");
    _pubX = pubX;
    _pubY = pubY;
    seller = s;
    phase = stage.initialized;
    timeout = now + time;
}

function SellerRevealKey(uint256 privKey) allowed(seller,stage.initialized) public{
    (uint256 x,uint256 y) = derivePubKey(privKey);
    require(x == _pubX,"x wrong");
    require(y == _pubY,"y wrong");
    seller.transfer(address(this).balance);
    phase = stage.finished;
}

function refund() public{
    require (now > timeout,"timeout not reached");
    require(phase > stage.created,"stage wrong");
    buyer.transfer(address(this).balance);
    phase = stage.finished;
}
  /// @param privKey The private key
  /// @return (qx, qy) The Public Key
  function derivePubKey(uint256 privKey) public view returns (uint256, uint256) {
    return ec.ecMul(
      privKey,
      GX,
      GY,
      AA,
      PP
    );
  }
}