// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;  
pragma abicoder v2;

import "./libraries/balancer/BalancerFixedPoint.sol";

struct ExactInQueryParam{
    uint256 balanceIn;
    uint256 weightIn;
    uint256 balanceOut;
    uint256 weightOut;
    uint256 amountIn;
}

/// @dev Swap Simulator for Balancer V2
contract BalancerSwapSimulator {    
    uint256 internal constant _MAX_IN_RATIO = 0.3e18;
	
    /// @dev reference https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/pool-weighted/contracts/WeightedMath.sol#L78
    function calcOutGivenIn(ExactInQueryParam memory _query) public pure returns (uint256) {	
        /**********************************************************************************************
        // outGivenIn                                                                                //
        // aO = amountOut                                                                            //
        // bO = balanceOut                                                                           //
        // bI = balanceIn              /      /            bI             \    (wI / wO) \           //
        // aI = amountIn    aO = bO * |  1 - | --------------------------  | ^            |          //
        // wI = weightIn               \      \       ( bI + aI )         /              /           //
        // wO = weightOut                                                                            //
        **********************************************************************************************/
        require(_query.amountIn <= BalancerFixedPoint.mulDown(_query.balanceIn, _MAX_IN_RATIO), '!maxIn');	
        uint256 denominator = BalancerFixedPoint.add(_query.balanceIn, _query.amountIn);
        uint256 base = BalancerFixedPoint.divUp(_query.balanceIn, denominator);
        uint256 exponent = BalancerFixedPoint.divDown(_query.weightIn, _query.weightOut);
        uint256 power = BalancerFixedPoint.powUp(base, exponent);

        return BalancerFixedPoint.mulDown(_query.balanceOut, BalancerFixedPoint.complement(power));
    }	

}