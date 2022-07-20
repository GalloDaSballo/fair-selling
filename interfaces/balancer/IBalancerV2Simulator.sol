// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;
pragma abicoder v2;

struct ExactInQueryParam{
    uint256 balanceIn;
    uint256 weightIn;
    uint256 balanceOut;
    uint256 weightOut;
    uint256 amountIn;
}

interface IBalancerV2Simulator {
    function calcOutGivenIn(ExactInQueryParam memory _query) external pure returns (uint256);
}