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
  uint time = 60 seconds; //template
  enum Stage {created, initialized,finished}
  EllipticCurve ec;
  address lib = {{ lib }};

  struct FileSaleSession {
          Stage stage;
          address payable seller;
          address payable buyer;
          uint pubX;
          uint pubY;
          uint balance;
          uint nextDeadline;
      }

  mapping (bytes32 => FileSaleSession) sessions;

    constructor() public {
        ec = EllipticCurve(lib);
    }
    
    modifier allowed(bytes32 sessionID, address caller, Stage stage) {
        require(sessions[sessionID].stage == stage);
        require(msg.sender == caller);
        require(block.timestamp  < sessions[sessionID].nextDeadline);
        _;
    }
    
function BuyerInitTrade(uint256 pubX,uint256 pubY, uint256 timeout, address payable s) payable public{
     bytes32 sessionID = calculateSessionID(msg.sender, s, pubY);
     require(sessions[sessionID].stage == Stage.created);

    sessions[sessionID] = FileSaleSession(
            Stage.initialized,
            s,
            msg.sender,
            pubX,
            pubY,
            msg.value,
            block.timestamp + timeout
        );
}

function SellerRevealKey(bytes32 sessionID, uint256 privKey) allowed(sessionID, sessions[sessionID].seller,Stage.initialized) public{
    (uint256 x,uint256 y) = derivePubKey(privKey);
    require(x == sessions[sessionID].pubX,"x wrong");
    require(y == sessions[sessionID].pubY,"y wrong");
    msg.sender.transfer(sessions[sessionID].balance);
    sessions[sessionID].stage = Stage.finished;
    
}

function refund(bytes32 sessionID) public{
    require (block.timestamp  > sessions[sessionID].nextDeadline,"timeout not reached");
    require(sessions[sessionID].stage == Stage.initialized,"stage wrong");
    sessions[sessionID].buyer.transfer(sessions[sessionID].balance);
    sessions[sessionID].stage = Stage.finished;
}

function calculateSessionID(address buyer, address seller, uint pubY) pure private returns(bytes32) {
        return keccak256(abi.encodePacked(seller, buyer, pubY));
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