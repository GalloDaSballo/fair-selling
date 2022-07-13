// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

enum SwapType { 
    CURVE, //0
    UNIV2, //1
    SUSHI, //2
    UNIV3, //3
    UNIV3WITHWETH, //4          [tokenIn -> WETH -> tokenOut]
    BALANCER, //5
    BALANCERWITHWETH, //6        [tokenIn -> WETH -> tokenOut]
	
    /// WETH<->USDC as connectors
    UNIV2WITHWETHUSDC, //7       [tokenIn -> WETH -> USDC -> tokenOut]
    UNIV2WITHUSDCWETH, //8       [tokenIn -> USDC -> WETH -> tokenOut]
    UNIV3WITHWETHUSDC, //9       [tokenIn -> WETH -> USDC -> tokenOut]
    UNIV3WITHUSDCWETH, //10      [tokenIn -> USDC -> WETH -> tokenOut]
    SUSHIWITHWETHUSDC, //11      [tokenIn -> WETH -> USDC -> tokenOut]
    SUSHIWITHUSDCWETH, //12      [tokenIn -> USDC -> WETH -> tokenOut]
	
    /// WETH<->WBTC as connectors
    UNIV2WITHWETHWBTC, //13      [tokenIn -> WETH -> WBTC -> tokenOut]
    UNIV2WITHWBTCWETH, //14      [tokenIn -> WBTC -> WETH -> tokenOut]
    UNIV3WITHWETHWBTC, //15      [tokenIn -> WETH -> WBTC -> tokenOut]
    UNIV3WITHWBTCWETH, //16      [tokenIn -> WBTC -> WETH -> tokenOut]
    SUSHIWITHWETHWBTC, //17      [tokenIn -> WETH -> WBTC -> tokenOut]
    SUSHIWITHWBTCWETH, //18      [tokenIn -> WBTC -> WETH -> tokenOut]
	
    /// Price Feed
    PRICEFEED //19
}

struct Quote {
    SwapType name;
    uint256 amountOut;
    bytes32[] pools; // specific pools involved in the optimal swap path
    uint256[] poolFees; // specific pool fees involved in the optimal swap path, typically in Uniswap V3
}

interface OnChainPricing {
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external returns (Quote memory);
	
    /// Following function are exposed to satisfy customized-quote requirement from callers 
    /// in case of some prior-knowledge or heuristic of the swap confirmed
    /// i.e., for BAL token related pricing, it would be good to try getBalancerPriceWithConnector() if necessary
	
    /// @dev Given the address of the input token & amount & the output token, 
    /// @dev try Uniswap V2 quote query by combining paths (input token ---> connector token A & connector token B ---> output token) 
    /// @dev with price feed between A and B (one of them is chosen as native token like WETH, another would be USDC or WBTC)
    function getUniPriceWithConnectorFeed(address router, address tokenIn, uint256 amountIn, address tokenOut, address connectorTokenA, address connectorTokenB) external view returns (uint256);
	
    /// @dev Given the address of the input token & amount & the output token, 
    /// @dev try Uniswap V3 quote query by combining paths (input token -> connector token A ~ connector token B -> output token) 
    /// @dev with price feed between A and B (one of them is chosen as native token like WETH, another would be USDC or WBTC)
    /// @return the quote for it with three hop fees: [tokenIn -> connectorTokenA] & [connectorTokenA -> connectorTokenB] & [connectorTokenB -> tokenOut]
    function getUniV3PriceWithConnectorFeed(address tokenIn, uint256 amountIn, address tokenOut, address connectorTokenA, address connectorTokenB) external returns (uint256, uint256, uint256, uint256);
	
    /// @dev Given the address of the input token & amount & the output token & connector token in between (input token ---> connector token ---> output token)
    /// @return the quote for it with two hop fees: [tokenIn -> connectorToken] & [connectorToken -> tokenOut], supported connector is WETH
    function getUniV3PriceWithConnector(address tokenIn, uint256 amountIn, address tokenOut, address connectorToken) external returns (uint256, uint256, uint256);	
	
    /// @dev Given the input/output/connector token, returns the quote for input amount from Balancer V2 and according poolIds for [tokenIn -> connectorToken] & [connectorToken -> tokenOut], supported connector is WETH
    function getBalancerPriceWithConnector(address tokenIn, uint256 amountIn, address tokenOut, address connectorToken) external returns (uint256, bytes32, bytes32);
}