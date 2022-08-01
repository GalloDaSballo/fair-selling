pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

enum SwapType { 
   CURVE, //0
   UNIV2, //1
   SUSHI, //2
   UNIV3, //3
   UNIV3WITHWETH, //4 
   BALANCER, //5
   BALANCERWITHWETH //6 
}

// Onchain Pricing Interface
struct Quote {
   SwapType name;
   uint256 amountOut;
   bytes32[] pools; // specific pools involved in the optimal swap path
   uint256[] poolFees; // specific pool fees involved in the optimal swap path, typically in Uniswap V3
}
interface OnChainPricing {
   function isPairSupported(address tokenIn, address tokenOut, uint256 amountIn) external view returns (bool);
   function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external view returns (Quote memory);
}
// END OnchainPricing

contract PricerWrapper {
   address public pricer;
   constructor(address _pricer) {
      pricer = _pricer;
   }
	
   function isPairSupported(address tokenIn, address tokenOut, uint256 amountIn) external view returns (bool) {
      return OnChainPricing(pricer).isPairSupported(tokenIn, tokenOut, amountIn);
   }

   function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external view returns (uint256, Quote memory) {
      uint256 _gasBefore = gasleft();
      Quote memory q = OnChainPricing(pricer).findOptimalSwap(tokenIn, tokenOut, amountIn);
      return (_gasBefore - gasleft(), q);
   }
}