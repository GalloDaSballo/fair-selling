// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/curve/ICurveRouter.sol";
import "../interfaces/pricer/IPricerV1.sol";

import {OnChainPricingMainnet} from "./OnChainPricingMainnet.sol";

/// @title OnChainPricingMainnetFeedConnectors
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev Mainnet Version of Price Quoter, hardcoded for more efficiency
/// @notice To spin a variant, just change the constants and use the Component Functions at the end of the file
/// @notice Instead of upgrading in the future, just point to a new implementation
/// @notice This version has enabled the resource-consuming quote paths like [tokenIn->connectorTokenA->connectoTokenB->tokenOut]
contract OnChainPricingMainnetFeedConnectors is OnChainPricingMainnet {

    // privileged to enable/disable resource-consuming quote paths
    address public constant TECH_OPS = 0x86cbD0ce0c087b482782c181dA8d191De18C8275;
    
    function setFeedConnectorsEnabled(bool _enable) external {
        require(msg.sender == TECH_OPS, "Only TechOps");
        feedConnectorsEnabled = _enable;
    }

    // === PRICING === //

    /// @dev find optimal quote with resource-consuming quote paths possibly enabled
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external override returns (Quote memory q) {
        q = _findOptimalSwap(tokenIn, tokenOut, amountIn);
    }
}