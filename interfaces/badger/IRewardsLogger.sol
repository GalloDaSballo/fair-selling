
// SPDX-License-Identifier: MIT

pragma solidity >=0.6.11;
pragma experimental ABIEncoderV2;

interface IRewardsLogger {
    function getUnlockSchedulesFor(address beneficiary, address token)
        external
        view
        returns (IRewardsLogger.UnlockSchedule[] memory);

    function setUnlockSchedule(
        address beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration
    ) external;

    struct UnlockSchedule {
        address beneficiary;
        address token;
        uint256 totalAmount;
        uint256 start;
        uint256 end;
        uint256 duration;
    }
}
