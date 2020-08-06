pragma solidity >=0.6.1;

import "bdtsim/protocol/delgado/delgado-trade/EllipticCurve.sol";


contract Delgado {

  uint256 public constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
  uint256 public constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
  uint256 public constant AA = 0;
  uint256 public constant BB = 7;
  uint256 public constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;
  enum Stage {created, initialized,finished}

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


    modifier allowed(bytes32 sessionID, address caller, Stage stage) {
        require(sessions[sessionID].stage == stage);
        require(msg.sender == caller);
        require(now < sessions[sessionID].nextDeadline);
        _;
    }
    
function BuyerInitTrade(uint256 pubX,uint256 pubY, uint time, address payable s) payable public{
     bytes32 sessionID = calculateSessionID(s,msg.sender, pubY);
     require(sessions[sessionID].stage == Stage.created);

    //require(msg.value >= price,"price wrong");
    sessions[sessionID] = FileSaleSession(
            Stage.initialized,
            s,
            msg.sender,
            pubX,
            pubY,
            msg.value,
            now + time);
}

function SellerRevealKey(bytes32 sessionID, uint256 privKey)  public allowed(sessionID, sessions[sessionID].seller ,Stage.initialized){
    (uint256 x,uint256 y) = derivePubKey(privKey);
    require(x == sessions[sessionID].pubX,"x wrong");
    require(y == sessions[sessionID].pubY,"y wrong");
    msg.sender.transfer(sessions[sessionID].balance);
    sessions[sessionID].stage = Stage.finished;
}

function refund(bytes32 sessionID) public{
    require (now > sessions[sessionID].nextDeadline,"timeout not reached");
    require(sessions[sessionID].stage >= Stage.initialized,"stage wrong");
    sessions[sessionID].buyer.transfer(sessions[sessionID].balance);
    sessions[sessionID].stage = Stage.finished;
}

function calculateSessionID(address buyer, address seller, uint pubY) pure private returns(bytes32) {
        return keccak256(abi.encodePacked(buyer, seller, pubY));
    }

  /// @param privKey The private key
  /// @return (qx, qy) The Public Key
  function derivePubKey(uint256 privKey) public pure returns (uint256, uint256) {
    return EllipticCurve.ecMul(
      privKey,
      GX,
      GY,
      AA,
      PP
    );
  }
}