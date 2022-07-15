// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.10;
pragma abicoder v2;

interface IUniswapV3Simulator {
    function simulateUniV3Swap(address _pool, address _token0, address _token1, bool _zeroForOne, uint24 _fee, uint256 _amountIn, uint256 _slippageAllowedBps) external view returns (uint256);
}