// SPDX-License-Identifier: GPL-2.0
pragma solidity 0.8.10;


import {ICurvePool} from "../interfaces/curve/ICurvePool.sol";
import {IHarvestForwarder} from "../interfaces/badger/IHarvestForwarder.sol";
import {IVault} from "../interfaces/badger/IVault.sol";
import {IBalancerVault} from "../interfaces/balancer/IBalancerVault.sol";
import {IAsset} from "../interfaces/balancer/IAsset.sol";
import {CowSwapSeller} from "./CowSwapSeller.sol";
import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


/// @title AuraBribesProcessor
/// @author Swole @ BadgerDAO
/// @dev BribesProcess for bveAura, using CowSwapSeller allows to process bribes fairly
/// Minimizing the amount of power that the manager can have
/// @notice This code is forked from the VotiumBribesProcessor
///     Original Version: https://github.com/GalloDaSballo/fair-selling/blob/main/contracts/VotiumBribesProcessor.sol
contract AuraBribesProcessor is CowSwapSeller {
    using SafeERC20 for IERC20;

    // All events are token / amount
    event SentBribeToGovernance(address indexed token, uint256 amount);
    event SentBribeToTree(address indexed token, uint256 amount);
    event PerformanceFeeGovernance(address indexed token, uint256 amount);
    event BribeEmission(address indexed token, address indexed recipient, uint256 amount);

    // address public manager /// inherited by CowSwapSeller

    // timestamp of last action, we allow anyone to sweep this contract
    // if admin has been idle for too long.
    // Sweeping simply emits to the badgerTree making fair emission to vault depositors
    // Once BadgerRewards is live we will integrate it
    uint256 public lastBribeAction;

    uint256 public constant MAX_MANAGER_IDLE_TIME = 10 days; // Because we have Strategy Notify, 10 days is enough
    // Way more time than expected

    IERC20 public constant BADGER = IERC20(0x3472A5A71965499acd81997a54BBA8D852C6E53d);
    IERC20 public constant AURA = IERC20(0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF);
    IERC20 public constant WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    address public constant STRATEGY = 0x3c0989eF27e3e3fAb87a2d7C38B35880C90E63b5;
    address public constant BADGER_TREE = 0x660802Fc641b154aBA66a62137e71f331B6d787A;

    // Source: https://badger.com/graviaura
    uint256 public constant MAX_BPS = 10_000;
    // A 5% fee will be charged on all bribes processed.
    uint256 public constant OPS_FEE = 500; // 5%

    /// `treasury_voter_multisig`
    /// https://github.com/Badger-Finance/badger-multisig/blob/6cd8f42ae0313d0da33a208d452370343e7599ba/helpers/addresses.py#L52
    address public constant TREASURY = 0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b;

    IVault public constant BVE_AURA = IVault(0xBA485b556399123261a5F9c95d413B4f93107407);

    // We send tokens to emit here
    IHarvestForwarder public constant HARVEST_FORWARDER = IHarvestForwarder(0xA84B663837D94ec41B0f99903f37e1d69af9Ed3E);

    /// NOTE: Need constructor for CowSwapSeller
    constructor(address _pricer) CowSwapSeller(_pricer) {}

    function notifyNewRound() external {
        require(msg.sender == STRATEGY);

        // Give the manager 10 days to process else anyone can claim
        lastBribeAction = block.timestamp;
    }


    /// === Security Function === ///

    /// @dev Emits all of token directly to tree for people to receive
    /// @param token The token to transfer
    /// @param sendToGovernance Should we send to the dev multisig, or emit directly to the badgerTree?
    /// @notice has built in expiration allowing anyone to send the tokens to tree should the manager stop processing bribes
    ///     can also sendToGovernance if you prefer
    ///     at this time both options have the same level of trust assumptions
    /// This is effectively a security rescue function
    /// The manager can call it to move funds to tree (forfeiting any fees)
    /// And anyone can rescue the funds if the manager goes rogue
    function ragequit(IERC20 token, bool sendToGovernance) external nonReentrant {
        bool timeHasExpired = block.timestamp > lastBribeAction + MAX_MANAGER_IDLE_TIME;
        require(msg.sender == manager || timeHasExpired);

        // In order to avoid selling after, set back the allowance to 0 to the Relayer
        token.safeApprove(address(RELAYER), 0);

        // Send all tokens to badgerTree without fee
        uint256 amount = token.balanceOf(address(this));
        if(sendToGovernance) {
            token.safeTransfer(DEV_MULTI, amount);
            emit SentBribeToGovernance(address(token), amount);
        } else {
            require(HARVEST_FORWARDER.badger_tree() == BADGER_TREE);

            // If manager rqs to emit in time, treasury still receives a fee
            if(!timeHasExpired && msg.sender == manager) {
                
                // Take a fee here
                uint256 fee = amount * OPS_FEE / MAX_BPS;
                token.safeTransfer(TREASURY, fee);

                emit PerformanceFeeGovernance(address(token), fee);

                amount -= fee;
            }

            // Emit to Tree
            token.safeApprove(address(HARVEST_FORWARDER), amount);
            HARVEST_FORWARDER.distribute(address(token), amount, address(BVE_AURA));

            emit SentBribeToTree(address(token), amount);
        }
    }

    /// === Day to Day Operations Functions === ///

    /// @dev
    /// Step 1
    /// Use sellBribeForWETH
    /// To sell all bribes to WETH
    /// @notice nonReentrant not needed as `_doCowswapOrder` is nonReentrant
    function sellBribeForWeth(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken != AURA); // Can't sell AURA;
        require(orderData.sellToken != BADGER); // Can't sell BADGER either;
        require(orderData.sellToken != WETH); // Can't sell WETH
        require(orderData.buyToken == WETH); // Gotta Buy WETH;

        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 2.a
    /// Swap WETH -> BADGER
    function swapWethForBadger(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken == WETH); // Must Sell WETH
        require(orderData.buyToken == BADGER); // Must Buy BADGER

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 2.b
    /// Swap WETH -> graviAURA or WETH -> AURA
    function swapWethForAURA(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken == WETH); // Must Sell WETH
        require(
            orderData.buyToken == AURA || 
            orderData.buyToken == IERC20(address(BVE_AURA))
        ); // Must buy AURA or BVE_AURA

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// AURA -> graviAURA -> Always Deposit in vault, unless direct pool

    /// @dev
    /// Step 3 Emit the Aura
    /// Takes all the Aura, takes fee, locks and emits it
    function swapAURATobveAURAAndEmit() external nonReentrant {
        // Will take all the Aura left,
        // swap it for bveAura if cheaper, or deposit it directly
        // and then emit it
        require(msg.sender == manager);
        require(HARVEST_FORWARDER.badger_tree() == BADGER_TREE);

        uint256 totalAURA = AURA.balanceOf(address(this));
        
        // === Handling of AURA === //
        if(totalAURA > 0) {
            // We'll also deposit the AURA
            AURA.safeIncreaseAllowance(address(BVE_AURA), totalAURA);
            // Deposit to address(this)
            BVE_AURA.deposit(totalAURA);

            // NOTE: Can be re-extended to use xyz stable pool (just use try/catch and expect long term failure)
        }

        // === Emit bveAURA === //
        uint256 totalBveAURA = BVE_AURA.balanceOf(address(this));
        require(totalBveAURA > 0);

        uint256 ops_fee = totalBveAURA * OPS_FEE / MAX_BPS;
        IERC20(address(BVE_AURA)).safeTransfer(TREASURY, ops_fee);

        // Subtraction to avoid dust
        uint256 toEmit = totalBveAURA - ops_fee;

        // Emit token to tree via HARVEST_FORWARDER
        IERC20(address(BVE_AURA)).safeIncreaseAllowance(address(HARVEST_FORWARDER), toEmit);
        HARVEST_FORWARDER.distribute(address(BVE_AURA), toEmit, address(BVE_AURA));

        emit PerformanceFeeGovernance(address(BVE_AURA), ops_fee);
        emit BribeEmission(address(BVE_AURA), address(BVE_AURA), toEmit);
    }

    /// @dev
    /// Step 4 Emit the Badger
    function emitBadger() external nonReentrant {
        require(msg.sender == manager);
        require(HARVEST_FORWARDER.badger_tree() == BADGER_TREE);

        // Sends Badger to the Tree
        // Emits custom event for it
        uint256 totalBadger = BADGER.balanceOf(address(this));
        require(totalBadger > 0);

        uint256 ops_fee = totalBadger * OPS_FEE / MAX_BPS;
        BADGER.safeTransfer(TREASURY, ops_fee);

        uint256 toEmitTotal = totalBadger - ops_fee;
        BADGER.safeIncreaseAllowance(address(HARVEST_FORWARDER), toEmitTotal);
        HARVEST_FORWARDER.distribute(address(BADGER), toEmitTotal, address(BVE_AURA));

        emit PerformanceFeeGovernance(address(BADGER), ops_fee);
        emit BribeEmission(address(BADGER), address(BVE_AURA), toEmitTotal);
    }


    /// === EXTRA === ///

    /// @dev Set new allowance to the relayer
    /// @notice used if you place two or more orders with the same token
    ///     In that case, place all orders, then set allowance to the sum of all orders
    function setCustomAllowance(address token, uint256 newAllowance) external nonReentrant {
        require(msg.sender == manager);

        IERC20(token).safeApprove(RELAYER, 0);
        // NOTE: Set this to the amount you need SUM(all_orders) to ensure they all go through
        IERC20(token).safeApprove(RELAYER, newAllowance);
    }
}
