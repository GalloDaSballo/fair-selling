// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0;
pragma experimental ABIEncoderV2;


interface ICurvePool {
  function coins(uint256 n) external view returns (address);
  function calc_token_amount(uint256[2] memory _amounts, bool _is_deposit) external returns (uint256);
  function exchange(int128 i, int128 j, uint256 _dx, uint256 _min_dy) external returns (uint256);
}