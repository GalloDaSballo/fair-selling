// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {IERC20Metadata} from "@oz/token/ERC20/extensions/IERC20Metadata.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";
import {Address} from "@oz/utils/Address.sol";


import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/uniswap/IV3Pool.sol";
import "../interfaces/uniswap/IV3Quoter.sol";
import "../interfaces/curve/ICurveRouter.sol";

/// @title OnChainPricing
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev Mainnet Version of Price Quoter, hardcoded for more efficiency
/// @notice To spin a variant, just change the constants and use the Component Functions at the end of the file
/// @notice Instead of upgrading in the future, just point to a new implementation
contract OnChainPricingMainnet {
    using Address for address;
    
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
		
    // UniV3 impl credit to https://github.com/1inch/spot-price-aggregator/blob/master/contracts/oracles/UniswapV3Oracle.sol
    address public constant UNIV3_QUOTER = 0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6;
    bytes32 public constant UNIV3_POOL_INIT_CODE_HASH = 0xe34f199b19b2b4f47f68442619d555527d244f78a3297ea89325f843f87b8b54;
    address public constant UNIV3_FACTORY = 0x1F98431c8aD98523631AE4a59f267346ea31F984;
    uint24[4] univ3_fees = [uint24(100), 500, 3000, 10000];

    struct Quote {
        string name;
        uint256 amountOut;
    }

    /// @dev View function for testing the routing of the strategy
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external returns (Quote memory) {
        bool wethInvolved = (tokenIn == WETH || tokenOut == WETH);
        uint256 length = wethInvolved? 4 : 5; // Add length you need

        Quote[] memory quotes = new Quote[](length);

        uint256 curveQuote = getCurvePrice(CURVE_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[0] = Quote("curve", curveQuote);

        uint256 uniQuote = getUniPrice(UNIV2_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[1] = Quote("uniV2", uniQuote);

        uint256 sushiQuote = getUniPrice(SUSHI_ROUTER, tokenIn, tokenOut, amountIn);
        quotes[2] = Quote("sushi", sushiQuote);

        uint256 univ3Quote = getUniV3Price(tokenIn, amountIn, tokenOut);
        quotes[3] = Quote("uniV3", univ3Quote);

        if(!wethInvolved){
            uint256 univ3WithWETHQuote = getUniV3PriceWithConnector(tokenIn, amountIn, tokenOut, WETH);
            quotes[4] = Quote("uniV3WithWETH", univ3WithWETHQuote);		
        }

        /// NOTE: Balancer is in V2
        

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


        // TODO: Consider doing check before revert to avoid paying extra gas
        // Specifically, test gas if we get revert vs if we check to avoid it
        try IUniswapRouterV2(router).getAmountsOut(amountIn, path) returns (uint256[] memory amounts) {
            quote = amounts[amounts.length - 1]; // Last one is the outToken
        } catch (bytes memory) {
            // We ignore as it means it's zero
        }

        return quote;
    }	  
	
    /// @dev Given the address of the input token & amount & the output token
    /// @return the quote for it
    function getUniV3Price(address tokenIn, uint256 amountIn, address tokenOut) public returns (uint256) {
        uint256 quoteRate;
		
        (address token0, address token1, bool token0Price) = _ifUniV3Token0Price(tokenIn, tokenOut);
        uint256 feeTypes = univ3_fees.length;
        for (uint256 i = 0; i < feeTypes; ++i){	
             //filter out disqualified pools to save gas on quoter swap query
             uint256 rate = _getUniV3Rate(token0, token1, univ3_fees[i], token0Price, amountIn);		
             if (rate > 0){
                 uint256 quote = _getUniV3QuoterQuery(tokenIn, tokenOut, univ3_fees[i], amountIn);
                 if (quote > quoteRate){
                     quoteRate = quote;				
                 }
             }
        }
		
        return quoteRate;
    }
	
    /// @dev Given the address of the input token & amount & the output token & connector token in between (input token ---> connector token ---> output token)
    /// @return the quote for it
    function getUniV3PriceWithConnector(address tokenIn, uint256 amountIn, address tokenOut, address connectorToken) public returns (uint256) {
        uint256 connectorAmount = getUniV3Price(tokenIn, amountIn, connectorToken);	
        if (connectorAmount > 0){	
            return getUniV3Price(connectorToken, connectorAmount, tokenOut);
        } else{
            return 0;
        }
    }
	
    /// @dev query swap result from Uniswap V3 quoter for given tokenIn -> tokenOut with amountIn & fee
    function _getUniV3QuoterQuery(address tokenIn, address tokenOut, uint24 fee, uint256 amountIn) internal returns (uint256){
        uint256 quote = IV3Quoter(UNIV3_QUOTER).quoteExactInputSingle(tokenIn, tokenOut, fee, amountIn, 0);
        return quote;
    }
	
    /// @dev return token0 & token1 and if token0 equals tokenIn
    function _ifUniV3Token0Price(address tokenIn, address tokenOut) internal pure returns (address, address, bool){
        (address token0, address token1) = tokenIn < tokenOut ? (tokenIn, tokenOut) : (tokenOut, tokenIn);
        return (token0, token1, token0 == tokenIn);
    }
	
    /// @dev Given the address of the input token & the output token & fee tier 
    /// @dev with trade amount & indicator if token0 pricing required (token1/token0 e.g., token0 -> token1)
    /// @dev note there are some heuristic checks around the price like pool reserve should satisfy the swap amount
    /// @return the current price in V3 for it
    function _getUniV3Rate(address token0, address token1, uint24 fee, bool token0Price, uint256 amountIn) internal view returns (uint256) {
	
        // heuristic check0: ensure the pool [exist] and properly initiated
        address pool = _getUniV3PoolAddress(token0, token1, fee);
        if (!pool.isContract() || IUniswapV3Pool(pool).liquidity() == 0) {
            return 0;
        }
		
        // heuristic check1: ensure the pool tokenIn reserve makes sense in terms of [amountIn]
        if (IERC20(token0Price? token0 : token1).balanceOf(pool) <= amountIn){
            return 0;	
        }

        // heuristic check2: ensure the pool tokenOut reserve makes sense in terms of the [amountOutput based on slot0 price]
        uint256 rate = _queryUniV3PriceWithSlot(token0, token1, pool, token0Price);
        uint256 amountOutput = rate * amountIn * (10 ** IERC20Metadata(token0Price? token1 : token0).decimals()) / (10 ** IERC20Metadata(token0Price? token0 : token1).decimals()) / 1e18;
        if (IERC20(token0Price? token1 : token0).balanceOf(pool) <= amountOutput){
            return 0;		
        }
		
        // heuristic check3: ensure the pool [reserve comparison is consistent with the slot0 price comparison], i.e., asset in less amount should be more expensive in AMM pool
        bool token0MoreExpensive = _compareUniV3Tokens(token0Price, rate);
        bool token0MoreReserved = _compareUniV3TokenReserves(token0, token1, pool);
        if (token0MoreExpensive == token0MoreReserved){
            return 0;		
        }
        
        return rate;
    }
	
    /// @dev query current price from V3 pool interface(slot0) with given pool & token0 & token1
    /// @dev and indicator if token0 pricing required (token1/token0 e.g., token0 -> token1)
    ///	@return the price of required token scaled with 1e18
    function _queryUniV3PriceWithSlot(address token0, address token1, address pool, bool token0Price) internal view returns (uint256) {			
        (uint256 sqrtPriceX96,,,,,,) = IUniswapV3Pool(pool).slot0();
        uint256 rate;
        if (token0Price) {
            rate = (((10 ** IERC20Metadata(token0).decimals() * sqrtPriceX96 >> 96) * sqrtPriceX96) >> 96) * 1e18 / 10 ** IERC20Metadata(token1).decimals();
        } else {
            rate = ((10 ** IERC20Metadata(token1).decimals() << 192) / sqrtPriceX96 / sqrtPriceX96) * 1e18 / 10 ** IERC20Metadata(token0).decimals();
        }
        return rate;
    }
	
    /// @dev check if token0 is more expensive than token1 given slot0 price & if token0 pricing required
    function _compareUniV3Tokens(bool token0Price, uint256 rate) internal view returns (bool) {
        return token0Price? (rate > 1e18) : (rate < 1e18);
    }
	
    /// @dev check if token0 reserve is bigger than token1 reserve
    function _compareUniV3TokenReserves(address token0, address token1, address pool) internal view returns (bool) {
        uint256 token0Num = IERC20(token0).balanceOf(pool) / (10 ** IERC20Metadata(token0).decimals());
        uint256 token1Num = IERC20(token1).balanceOf(pool) / (10 ** IERC20Metadata(token1).decimals());
        return token0Num > token1Num;
    }
	
    /// @dev query with the address of the token0 & token1 & the fee tier
    /// @return the uniswap v3 pool address
    function _getUniV3PoolAddress(address token0, address token1, uint24 fee) internal pure returns (address) {
        bytes32 addr = keccak256(abi.encodePacked(hex'ff', UNIV3_FACTORY, keccak256(abi.encode(token0, token1, fee)), UNIV3_POOL_INIT_CODE_HASH));
        return address(uint160(uint256(addr)));
    }

    // TODO: Consider adding a `bool` check for `isWeth` to skip the weth check (as it's computed above)
    // TODO: Most importantly need to run some gas cost tests to ensure we keep at most at like 120k


    /// @dev Given the address of the CurveLike Router, the input amount, and the path, returns the quote for it
    function getCurvePrice(address router, address tokenIn, address tokenOut, uint256 amountIn) public view returns (uint256) {
        (, uint256 curveQuote) = ICurveRouter(router).get_best_rate(tokenIn, tokenOut, amountIn);

        return curveQuote;
    }
}