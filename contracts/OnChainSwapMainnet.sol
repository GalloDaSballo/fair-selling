// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";

import "../interfaces/uniswap/IUniswapRouterV3.sol";
import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/curve/ICurveRouter.sol";
import "../interfaces/balancer/IBalancerV2Vault.sol";

/// @dev Mainnet Version of swap for various on-chain dex
contract OnChainSwapMainnet {
    using SafeERC20 for IERC20;

    address public constant UNIV3_ROUTER = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45; 
    address public constant CURVE_ROUTER = 0x8e764bE4288B842791989DB5b8ec067279829809; 
    address public constant BALANCERV2_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8; 

    /// @dev function for swap in Uniswap V3
    /// @dev path: (abi.encodePacked) for (tokenIn, fee, connectorToken, fee, tokenOut)
    /// @dev fee is in hundredths of basis points (e.g. the fee for a pool at the 0.3% tier is 3000; the fee for a pool at the 0.01% tier is 100).
    function execSwapUniV3(uint256 amountIn, address tokenIn, bytes calldata abiEncodePackedPath, uint256 expectedOut, address receiver) external returns (uint256) {
        IERC20(tokenIn).safeApprove(UNIV3_ROUTER, 0);
        IERC20(tokenIn).safeApprove(UNIV3_ROUTER, amountIn);
		
        ExactInputParams memory params = ExactInputParams({
                path: abiEncodePackedPath,
                recipient: receiver,
                amountIn: amountIn,
                amountOutMinimum: expectedOut
        });
        return IUniswapRouterV3(UNIV3_ROUTER).exactInput(params);
    }
	
    // @dev function for single-hop path encode in Uniswap V3
    function encodeUniV3SingleHop(address tokenIn, uint24 fee, address tokenOut) external pure returns (bytes memory) {        
        return abi.encodePacked(tokenIn, fee, tokenOut);
    }
	
    // @dev function for two-hop path encode in Uniswap V3
    function encodeUniV3TwoHop(address tokenIn, uint24 fee1, address connectorToken, uint24 fee2, address tokenOut) external pure returns (bytes memory) {        
        return abi.encodePacked(tokenIn, fee1, connectorToken, fee2, tokenOut);
    }

    /// @dev function for swap in Uniswap V2 alike dex
    function execSwapUniV2(address router, uint256 amountIn, address[] calldata path, uint256 expectedOut, address receiver) external returns (uint256) {
        IERC20(path[0]).safeApprove(router, 0);
        IERC20(path[0]).safeApprove(router, amountIn);
		
        uint256[] memory _amountsOut = IUniswapRouterV2(router).swapExactTokensForTokens(amountIn, expectedOut, path, receiver, block.timestamp);
        return _amountsOut[_amountsOut.length - 1];
    }

    /// @dev function for swap in Curve
    function execSwapCurve(address pool, uint256 amountIn, address tokenIn, address tokenOut, uint256 expectedOut, address receiver) external returns (uint256) {
        IERC20(tokenIn).safeApprove(CURVE_ROUTER, 0);
        IERC20(tokenIn).safeApprove(CURVE_ROUTER, amountIn);
		
        return ICurveRouter(CURVE_ROUTER).exchange(pool, tokenIn, tokenOut, amountIn, expectedOut, receiver);
    }

    /// @dev function for swap in Balancer V2 in a single pool
    function execSwapBalancerV2Single(bytes32 poolID, uint256 amountIn, address tokenIn, address tokenOut, uint256 expectedOut, address receiver) external returns (uint256) {
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, 0);
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, amountIn);
		
        SingleSwap memory singleSwap = SingleSwap(poolID, SwapKind.GIVEN_IN, tokenIn, tokenOut, amountIn, "");
        FundManagement memory funds = FundManagement(address(this), false, receiver, false);		
        return IBalancerV2Vault(BALANCERV2_VAULT).swap(singleSwap, funds, expectedOut, block.timestamp);
    }

    /// @dev function for swap in Balancer V2 across 2 pools via connectorToken in between
    /// @dev It is good practice to account for slippage, e.g., if we are performing a GIVEN_IN batchSwap and wanted to apply a 1% slippage tolerance, 
    /// @dev we could multiply the original expectedOut from `queryBatchSwap` by 0.99
    function execSwapBalancerV2Batch(bytes32 firstPoolId, bytes32 secondPoolId, uint256 amountIn, address tokenIn, address tokenOut, address connectorToken, uint256 expectedOut, address receiver) external returns (uint256) {
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, 0);
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, amountIn);
		
        address[] memory assets = new address[](3);
        assets[0] = tokenIn;
        assets[1] = connectorToken;
        assets[2] = tokenOut;

        BatchSwapStep[] memory swaps = new BatchSwapStep[](2);
        swaps[0] = BatchSwapStep(firstPoolId, 0, 1, amountIn, "");
        swaps[1] = BatchSwapStep(secondPoolId, 1, 2, 0, "");// amount == 0 means use all from previous step

        FundManagement memory funds = FundManagement(address(this), false, receiver, false);
		
        // If the amount to be transferred for a given asset is greater than its limit, the trade will fail with error BAL#507: SWAP_LIMIT.
        int256[] memory limits = new int256[](3);
        limits[0] = int256(amountIn);
        limits[1] = 0;// for connectorToken
        limits[2] = 0 - int256(expectedOut);
		
        int256[] memory _deltas = IBalancerV2Vault(BALANCERV2_VAULT).batchSwap(SwapKind.GIVEN_IN, swaps, assets, funds, limits, block.timestamp);
        return uint256(0 - _deltas[_deltas.length - 1]);
    }
}