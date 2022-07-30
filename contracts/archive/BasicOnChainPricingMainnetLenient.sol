// SPDX-License-Identifier: GPL-2.0
pragma solidity 0.8.10;


import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


import "../../interfaces/uniswap/IUniswapRouterV2.sol";
import "../../interfaces/curve/ICurveRouter.sol";

// NOTE: Mostly here for archival
// https://etherscan.io/address/0xbab7f98d62479309219b2cc5026d4ad1c6c05674#code
// Used by VotiumBribesProcessor

/// @title OnChainPricing
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev Pricer V1
/// @dev Mainnet Version of Price Quoter, hardcoded for more efficiency
/// @notice To spin a variant, just change the constants and use the Component Functions at the end of the file
/// @notice Instead of upgrading in the future, just point to a new implementation
/// @notice This version has 5% extra slippage to allow further flexibility
///     if the manager abuses the check you should consider reverting back to a more rigorous pricer
contract BasicOnChainPricingMainnetLenient {

    struct Quote {
        string name;
        uint256 amountOut;
    }
    
    // Assumption #1 Most tokens liquid pair is WETH (WETH is tokenized ETH for that chain)
    // e.g on Fantom, WETH would be wFTM
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    /// == Uni V2 Like Routers || These revert on non-existent pair == //
    // UniV2
    address public constant UNIV2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; // Spookyswap
    // Sushi
    address public constant SUSHI_ROUTER = 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F;

    // Curve / Doesn't revert on failure
    address public constant CURVE_ROUTER = 0x8e764bE4288B842791989DB5b8ec067279829809; // Curve quote and swaps

    // === SLIPPAGE === //
    // Can change slippage within rational limits
    address public constant TECH_OPS = 0x86cbD0ce0c087b482782c181dA8d191De18C8275;
    
    uint256 private constant MAX_BPS = 10_000;

    uint256 private constant MAX_SLIPPAGE = 500; // 5%

    uint256 public slippage = 200; // 2% Initially


    function setSlippage(uint256 newSlippage) external {
        require(msg.sender == TECH_OPS, "Only TechOps");
        require(newSlippage < MAX_SLIPPAGE);
        slippage = newSlippage;
    }

    // === PRICING === //

    /// @dev View function for testing the routing of the strategy
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external returns (Quote memory) {
        uint256 length = 3; // Add length you need

        Quote[] memory quotes = new Quote[](length);

        uint256 curveQuote = getCurvePrice(CURVE_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[0] = Quote("curve", curveQuote);

        uint256 uniQuote = getUniPrice(UNIV2_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[1] = Quote("uniV2", uniQuote);

        uint256 sushiQuote = getUniPrice(SUSHI_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[2] = Quote("sushi", sushiQuote);


        /// NOTE: Lack of Balancer and UniV3
        

        // Because this is a generalized contract, it is best to just loop,
        // Ideally we have a hierarchy for each chain to save some extra gas, but I think it's ok
        // O(n) complexity and each check is like 9 gas
        Quote memory bestQuote = quotes[0];
        unchecked {
            for(uint256 x = 1; x < length; ++x) {
                if(quotes[x].amountOut > bestQuote.amountOut) {
                    bestQuote = quotes[x];
                }
            }
        }

        bestQuote.amountOut = bestQuote.amountOut * (MAX_BPS - slippage) / MAX_BPS;
        return bestQuote;
    }
    

    /// === Component Functions === /// 
    /// Why bother?
    /// Because each chain is slightly different but most use similar tech / forks
    /// May as well use the separate functoions so each OnChain Pricing on different chains will be slightly different
    /// But ultimately will work in the same way

    /// @dev Given the address of the UniV2Like Router, the input amount, and the path, returns the quote for it
    function getUniPrice(address router, address tokenIn, address tokenOut, uint256 amountIn) public view returns (uint256) {
        address[] memory path = new address[](2);
        path[0] = address(tokenIn);
        path[1] = address(tokenOut);

        uint256 quote; //0

        // Specifically, test gas if we get revert vs if we check to avoid it
        try IUniswapRouterV2(router).getAmountsOut(amountIn, path) returns (uint256[] memory amounts) {
            quote = amounts[amounts.length - 1]; // Last one is the outToken
        } catch (bytes memory) {
            // We ignore as it means it's zero
        }

        return quote;
    }

    /// @dev Given the address of the CurveLike Router, the input amount, and the path, returns the quote for it
    function getCurvePrice(address router, address tokenIn, address tokenOut, uint256 amountIn) public view returns (uint256) {
        (, uint256 curveQuote) = ICurveRouter(router).get_best_rate(tokenIn, tokenOut, amountIn);

        return curveQuote;
    }
}