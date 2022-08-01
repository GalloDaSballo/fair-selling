// SPDX-License-Identifier: GPL-2.0
pragma solidity 0.8.10;

import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";

import "../interfaces/uniswap/IUniswapRouterV3.sol";
import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/curve/ICurveRouter.sol";
import "../interfaces/balancer/IBalancerV2Vault.sol";

/**
    NOTE: UNSAFE, UNTESTED, WIP, Use, read, look at and copy at your own risk
 */

enum SwapType { 
    CURVE, //0
    UNIV2, //1
    SUSHI, //2
    UNIV3, //3
    UNIV3WITHWETH, //4 
    BALANCER, //5
    BALANCERWITHWETH //6 
}

struct Quote {
    SwapType name;
    uint256 amountOut;
    bytes32[] pools; // specific pools involved in the optimal swap path
    uint256[] poolFees; // specific pool fees involved in the optimal swap path, typically in Uniswap V3
}

interface OnChainPricing {
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external view returns (Quote memory);
}

/// @dev Mainnet Version of swap for various on-chain dex
contract OnChainSwapMainnet {
    using SafeERC20 for IERC20;

    address public constant UNIV3_ROUTER = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45; 
    address public constant CURVE_ROUTER = 0x8e764bE4288B842791989DB5b8ec067279829809; 
    address public constant BALANCERV2_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8; 
    address public constant UNIV2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; 
    address public constant SUSHI_ROUTER = 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F;
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2; 
	
    uint256 public SWAP_SLIPPAGE_TOLERANCE = 500; // initially 5%
    uint256 public constant SWAP_SLIPPAGE_MAX = 10000;
		
    address public constant TECH_OPS = 0x86cbD0ce0c087b482782c181dA8d191De18C8275;
    address public pricer;

    function setSwapSlippageTolerance(uint256 _slippage) external {
        require(msg.sender == TECH_OPS, "!TechOps");
        require(_slippage < SWAP_SLIPPAGE_MAX, "!_slippage");
        SWAP_SLIPPAGE_TOLERANCE = _slippage;
    }		

    function setPricer(address _pricer) external {
        require(msg.sender == TECH_OPS, "!TechOps");
        require(_pricer != address(0), "!_pricer");
        pricer = _pricer;
    }		
		
    /// @dev execute on-chain swap based on optimal quote
    /// @return output amount after swap execution
    function doOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external returns(uint256){
        require(pricer != address(0), "!pricer");
        Quote memory _optimalQuote = OnChainPricing(pricer).findOptimalSwap(tokenIn, tokenOut, amountIn);
        return doOptimalSwapWithQuote(tokenIn, tokenOut, amountIn, _optimalQuote);
    }
		
    /// @dev execute on-chain swap based on optimal quote from OnChainPricingMainnet#findOptimalSwap
    /// @return output amount after swap execution
    function doOptimalSwapWithQuote(address tokenIn, address tokenOut, uint256 amountIn, Quote memory optimalQuote) public returns(uint256){		
        SwapType dex = optimalQuote.name;
        uint256 _minOut = optimalQuote.amountOut * (SWAP_SLIPPAGE_MAX - SWAP_SLIPPAGE_TOLERANCE) / SWAP_SLIPPAGE_MAX;
		
        if (dex == SwapType.CURVE){
            return execSwapCurve(convertToAddress(optimalQuote.pools[0]), amountIn, tokenIn, tokenOut, _minOut, msg.sender);
        }else if (dex == SwapType.UNIV2){
            address[] memory path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
            return execSwapUniV2(UNIV2_ROUTER, amountIn, path, _minOut, msg.sender);			
        }else if (dex == SwapType.SUSHI){
            address[] memory path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
            return execSwapUniV2(SUSHI_ROUTER, amountIn, path, _minOut, msg.sender);		
        }else if (dex == SwapType.UNIV3){
            bytes memory encodedPath = encodeUniV3SingleHop(tokenIn, uint24(optimalQuote.poolFees[0]), tokenOut);
            return execSwapUniV3(amountIn, tokenIn, encodedPath, _minOut, msg.sender);
        }else if (dex == SwapType.UNIV3WITHWETH){
            bytes memory encodedPath = encodeUniV3TwoHop(tokenIn, uint24(optimalQuote.poolFees[0]), WETH, uint24(optimalQuote.poolFees[1]), tokenOut);
            return execSwapUniV3(amountIn, tokenIn, encodedPath, _minOut, msg.sender);		
        }else if (dex == SwapType.BALANCER){
            return execSwapBalancerV2Single(optimalQuote.pools[0], amountIn, tokenIn, tokenOut, _minOut, msg.sender);
        }else if (dex == SwapType.BALANCERWITHWETH){
            return execSwapBalancerV2Batch(optimalQuote.pools[0], optimalQuote.pools[1], amountIn, tokenIn, tokenOut, WETH, _minOut, msg.sender);
        }else{
            return 0;
        }
    }

    /// @dev function for swap in Uniswap V3
    /// @dev path: (abi.encodePacked) for (tokenIn, fee, connectorToken, fee, tokenOut)
    /// @dev fee is in hundredths of basis points (e.g. the fee for a pool at the 0.3% tier is 3000; the fee for a pool at the 0.01% tier is 100).
    function execSwapUniV3(uint256 amountIn, address tokenIn, bytes memory abiEncodePackedPath, uint256 expectedOut, address receiver) public returns (uint256) {
        IERC20(tokenIn).safeApprove(UNIV3_ROUTER, 0);
        IERC20(tokenIn).safeApprove(UNIV3_ROUTER, amountIn);
		
        require(_checkTokenTransfer(tokenIn, amountIn), "!AMT");
		
        ExactInputParams memory params = ExactInputParams({
                path: abiEncodePackedPath,
                recipient: receiver,
                amountIn: amountIn,
                amountOutMinimum: expectedOut
        });
        return IUniswapRouterV3(UNIV3_ROUTER).exactInput(params);
    }
	
    /// @dev function for single-hop path encode in Uniswap V3
    function encodeUniV3SingleHop(address tokenIn, uint24 fee, address tokenOut) public pure returns (bytes memory) {        
        return abi.encodePacked(tokenIn, fee, tokenOut);
    }
	
    /// @dev function for two-hop path encode in Uniswap V3
    function encodeUniV3TwoHop(address tokenIn, uint24 fee1, address connectorToken, uint24 fee2, address tokenOut) public pure returns (bytes memory) {        
        return abi.encodePacked(tokenIn, fee1, connectorToken, fee2, tokenOut);
    }
	
    function convertToAddress(bytes32 _input) public pure returns (address) {
        return address(uint160(bytes20(_input)));
    }

    /// @dev function for swap in Uniswap V2 alike dex
    function execSwapUniV2(address router, uint256 amountIn, address[] memory path, uint256 expectedOut, address receiver) public returns (uint256) {
        IERC20(path[0]).safeApprove(router, 0);
        IERC20(path[0]).safeApprove(router, amountIn);
		
        require(_checkTokenTransfer(path[0], amountIn), "!AMT");
		
        uint256[] memory _amountsOut = IUniswapRouterV2(router).swapExactTokensForTokens(amountIn, expectedOut, path, receiver, block.timestamp);
        return _amountsOut[_amountsOut.length - 1];
    }

    /// @dev function for swap in Curve
    function execSwapCurve(address pool, uint256 amountIn, address tokenIn, address tokenOut, uint256 expectedOut, address receiver) public returns (uint256) {
        IERC20(tokenIn).safeApprove(CURVE_ROUTER, 0);
        IERC20(tokenIn).safeApprove(CURVE_ROUTER, amountIn);
		
        require(_checkTokenTransfer(tokenIn, amountIn), "!AMT");
		
        return ICurveRouter(CURVE_ROUTER).exchange(pool, tokenIn, tokenOut, amountIn, expectedOut, receiver);
    }

    /// @dev function for swap in Balancer V2 in a single pool
    function execSwapBalancerV2Single(bytes32 poolID, uint256 amountIn, address tokenIn, address tokenOut, uint256 expectedOut, address receiver) public returns (uint256) {
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, 0);
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, amountIn);
		
        require(_checkTokenTransfer(tokenIn, amountIn), "!AMT");
		
        SingleSwap memory singleSwap = SingleSwap(poolID, SwapKind.GIVEN_IN, tokenIn, tokenOut, amountIn, "");
        FundManagement memory funds = FundManagement(address(this), false, receiver, false);		
        return IBalancerV2Vault(BALANCERV2_VAULT).swap(singleSwap, funds, expectedOut, block.timestamp);
    }

    /// @dev function for swap in Balancer V2 across 2 pools via connectorToken in between
    /// @dev It is good practice to account for slippage, e.g., if we are performing a GIVEN_IN batchSwap and wanted to apply a 1% slippage tolerance, 
    /// @dev we could multiply the original expectedOut from `queryBatchSwap` by 0.99
    function execSwapBalancerV2Batch(bytes32 firstPoolId, bytes32 secondPoolId, uint256 amountIn, address tokenIn, address tokenOut, address connectorToken, uint256 expectedOut, address receiver) public returns (uint256) {
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, 0);
        IERC20(tokenIn).safeApprove(BALANCERV2_VAULT, amountIn);
		
        require(_checkTokenTransfer(tokenIn, amountIn), "!AMT");
		
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
	
    /// @dev caller needs to 'push' the amount of token for swap to this contract
    /// @return if token balance already in this contract satisfy expected given-in amount for the swap
    function _checkTokenTransfer(address token, uint256 value) internal returns (bool){
        return IERC20(token).balanceOf(address(this)) >= value;
    }

}