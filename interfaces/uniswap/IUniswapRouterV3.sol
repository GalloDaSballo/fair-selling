// SPDX-License-Identifier: MIT
pragma solidity >=0.7.5;
pragma abicoder v2;

//A path is a sequence of token addresses and poolFees that define the pools used in the swaps.
//The format for pool encoding(abi.abiEncodedPath) is (tokenIn, fee, connectorToken, fee, tokenOut) where connectorToken parameter is the shared token across the pools.
//For example, if we are swapping DAI to USDC and then USDC to WETH the path encoding is (DAI, 0.3%, USDC, 0.3%, WETH).
//and the path should be encoded like `abi.encodePacked(DAI, 3000, USDC, 3000, WETH)`
//Note that fee is in hundredths of basis points (e.g. the fee for a pool at the 0.3% tier is 3000; the fee for a pool at the 0.01% tier is 100).
struct ExactInputParams {
    bytes path;
    address recipient;
    uint256 amountIn;
    uint256 amountOutMinimum;
}

// https://github.com/Uniswap/swap-router-contracts/blob/v1.1.0/contracts/interfaces/IV3SwapRouter.sol
// https://docs.uniswap.org/protocol/reference/deployments
interface IUniswapRouterV3 {
    function exactInput(ExactInputParams calldata params) external returns (uint256 amountOut);
}
