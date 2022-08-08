// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;
pragma abicoder v2;

enum BalancerV2SwapKind { GIVEN_IN, GIVEN_OUT }

struct BalancerV2BatchSwapStep {
    bytes32 poolId;
    uint256 assetInIndex;
    uint256 assetOutIndex;
    uint256 amount;
    bytes userData;
}

struct BalancerV2FundManagement {
    address sender;
    bool fromInternalBalance;
    address recipient;
    bool toInternalBalance;
}

interface IBalancerV2VaultQuoter {
    function queryBatchSwap(BalancerV2SwapKind kind, BalancerV2BatchSwapStep[] calldata swaps, address[] calldata assets, BalancerV2FundManagement calldata funds) external returns (int256[] memory assetDeltas);
}

// gas consuming quoter https://dev.balancer.fi/resources/query-how-much-x-for-y
library BalancerQuoter {
    address private constant _vault = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
	
    function getBalancerPriceWithinPool(bytes32 poolId, address tokenIn, uint256 amountIn, address tokenOut) public returns (uint256) {	
		
        address[] memory assets = new address[](2);
        assets[0] = tokenIn;
        assets[1] = tokenOut;
		
        BalancerV2BatchSwapStep[] memory swaps = new BalancerV2BatchSwapStep[](1);
        swaps[0] = BalancerV2BatchSwapStep(poolId, 0, 1, amountIn, "");
		
        BalancerV2FundManagement memory funds = BalancerV2FundManagement(address(this), false, address(this), false);
		
        int256[] memory assetDeltas = IBalancerV2VaultQuoter(_vault).queryBatchSwap(BalancerV2SwapKind.GIVEN_IN, swaps, assets, funds);

        // asset deltas: either transferring assets from the sender (for positive deltas) or to the recipient (for negative deltas).
        return assetDeltas.length > 0 ? uint256(0 - assetDeltas[assetDeltas.length - 1]) : 0;
    }
	
    /// @dev Given the input/output/connector token, returns the quote for input amount from Balancer V2
    function getBalancerPriceWithConnector(bytes32 firstPoolId, bytes32 secondPoolId, address tokenIn, uint256 amountIn, address tokenOut, address connectorToken) public returns (uint256) { 		
        address[] memory assets = new address[](3);
        assets[0] = tokenIn;
        assets[1] = connectorToken;
        assets[2] = tokenOut;
		
        BalancerV2BatchSwapStep[] memory swaps = new BalancerV2BatchSwapStep[](2);
        swaps[0] = BalancerV2BatchSwapStep(firstPoolId, 0, 1, amountIn, "");
        swaps[1] = BalancerV2BatchSwapStep(secondPoolId, 1, 2, 0, "");// amount == 0 means use all from previous step
		
        BalancerV2FundManagement memory funds = BalancerV2FundManagement(address(this), false, address(this), false);
		
        int256[] memory assetDeltas = IBalancerV2VaultQuoter(_vault).queryBatchSwap(BalancerV2SwapKind.GIVEN_IN, swaps, assets, funds);

        // asset deltas: either transferring assets from the sender (for positive deltas) or to the recipient (for negative deltas).
        return assetDeltas.length > 0 ? uint256(0 - assetDeltas[assetDeltas.length - 1]) : 0;    
    }
}