// SPDX-License-Identifier: MIT

pragma solidity >=0.6.12;
pragma experimental ABIEncoderV2;

interface IBadgerTreeV2 {
    function lastPublishTimestamp() external view returns (uint256);
}
