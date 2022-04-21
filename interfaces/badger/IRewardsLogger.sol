
// SPDX-License-Identifier: MIT

pragma solidity >=0.6.11;
pragma experimental ABIEncoderV2;

interface IRewardsLogger {    
  function setUnlockSchedule(
        address beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration
    ) external;
}