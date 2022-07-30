// SPDX-License-Identifier: GPL-2.0
pragma solidity 0.8.10;


import {ICurvePool} from "../../interfaces/curve/ICurvePool.sol";
import {ISettV4} from "../../interfaces/badger/ISettV4.sol";
import {CowSwapSeller} from "../CowSwapSeller.sol";
import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


/// @title TestProcessor
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev Test processor for rinkeby
contract TestProcessor is CowSwapSeller {
    using SafeERC20 for IERC20;

    constructor(address _pricer) CowSwapSeller(_pricer) {}


    /// @dev Recover tokens
    function sweep(address token) external {
        require(msg.sender == manager);
        IERC20(token).safeTransfer(manager, IERC20(token).balanceOf(address(this)));
    }


    function doCowswapOrder(Data calldata orderData, bytes memory orderUid) external {
        _doCowswapOrder(orderData, orderUid);
    }

    function cancelCowswapOrder(bytes memory orderUid) external {
        _cancelCowswapOrder(orderUid);
    }

}