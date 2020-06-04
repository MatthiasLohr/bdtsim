pragma solidity >=0.6.4;

import "./EllipticCurve.sol";


contract Delgado {

  uint256 public constant GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
  uint256 public constant GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
  uint256 public constant AA = 0;
  uint256 public constant BB = 7;
  uint256 public constant PP = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;
  uint256 _pubX;
  uint256 _pubY;
  address payable _s;
  uint time;
  uint amount;
  uint256 public constant timeout = 60;

  
function BuyerInitTrade(uint256 pubX,uint256 pubY, address payable s ) payable public{
    _pubX = pubX;
    _pubY = pubY;
    _s = s;
    time = now;
}

function SellerRevealKey(uint256 privKey) public{
    (uint256 x,uint256 y) = derivePubKey(privKey);
    require(x == _pubX);
    require(y == _pubY);

    _s.transfer(address(this).balance);
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