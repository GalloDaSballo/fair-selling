// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {IRewardsLogger} from "../interfaces/badger/IRewardsLogger.sol";
import {ICurvePool} from "../interfaces/curve/ICurvePool.sol";
import {ISettV4} from "../interfaces/badger/ISettV4.sol";
import {CowSwapSeller} from "./CowSwapSeller.sol";
import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


// Original Python Code: https://github.com/Badger-Finance/badger-multisig/blob/main/scripts/badger/swap_bribes_for_bvecvx.py#L39
// Architecture: https://miro.com/app/board/uXjVO9yyd7o=/


/// @title BribesProcessor
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev BribesProcess for bveCVX, using CowSwapSeller allows to process bribes fairly
/// Minimizing the amount of power that the manager can have
/// @notice This code is WIP, any feedback is appreciated alex@badger.finance
contract VotiumBribesProcessor is CowSwapSeller {
    using SafeERC20 for IERC20;


    // All events are token / amount
    event SentBribeToGovernance(address indexed token, uint256 amount);
    event SentBribeToTree(address indexed token, uint256 amount);
    event PerformanceFeeGovernance(address indexed token, uint256 amount);

    event TreeDistribution(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );

    // address public manager /// inherited by CowSwapSeller

    // timestamp of last action, we allow anyone to sweep this contract
    // if admin has been idle for too long.
    // Sweeping simply emits to the badgerTree making fair emission to vault depositors
    // Once BadgerRewards is live we will integrate it
    uint256 public lastBribeAction;

    uint256 public constant MAX_MANAGER_IDLE_TIME = 10 days; // Because we have Strategy Notify, 10 days is enough
    // Way more time than expected

    IERC20 public constant BADGER = IERC20(0x3472A5A71965499acd81997a54BBA8D852C6E53d);
    IERC20 public constant CVX = IERC20(0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B);
    IERC20 public constant WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    address public constant STRATEGY = 0x898111d1F4eB55025D0036568212425EE2274082;
    address public constant BADGER_TREE = 0x660802Fc641b154aBA66a62137e71f331B6d787A;
    address public constant CVX_BVE_CVX_SETT = 0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551;

    uint256 public constant MAX_BPS = 10_000;
    uint256 public constant BADGER_SHARE = 2750; //27.50%
    uint256 public constant OPS_FEE = 500; // 5%
    uint256 public constant LIQ_FEE = 500; // 5%

    /// `treasury_vault_multisig`
    /// https://github.com/Badger-Finance/badger-multisig/blob/9f04e0589b31597390f2115501462794baca2d4b/helpers/addresses.py#L38
    address public constant TREASURY = 0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e;

    // Badger Governance
    address public constant DEV_MULTI = 0xB65cef03b9B89f99517643226d76e286ee999e77;


    ISettV4 public constant BVE_CVX = ISettV4(0xfd05D3C7fe2924020620A8bE4961bBaA747e6305);
    ICurvePool public constant CVX_BVE_CVX_CURVE = ICurvePool(0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512);
    IRewardsLogger public constant REWARDS_LOGGER = IRewardsLogger(0x0A4F4e92C3334821EbB523324D09E321a6B0d8ec);

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

            // If manager rqs to emit in time, treasury still receives a fee
            if(!timeHasExpired && msg.sender == manager) {
                // Take a fee here

                uint256 fee = amount * OPS_FEE / MAX_BPS;
                token.safeTransfer(TREASURY, fee);

                emit PerformanceFeeGovernance(address(token), fee);

                amount -= fee;
            }

            token.safeTransfer(BADGER_TREE, amount);

            emit SentBribeToTree(address(token), amount);
            emit TreeDistribution(address(token), amount, block.number, block.timestamp);
        }
    }

    /// === Day to Day Operations Functions === ///

    /// @dev
    /// Step 1
    /// Use sellBribeForWETH
    /// To sell all bribes to WETH
    /// @notice nonReentrant not needed as `_doCowswapOrder` is nonReentrant
    function sellBribeForWeth(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken != CVX); // Can't sell CVX;
        require(orderData.sellToken != BADGER); // Can't sell BADGER either;
        require(orderData.sellToken != WETH); // Can't sell WETH
        require(orderData.buyToken == WETH); // Gotta Buy WETH;

        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 2.a
    /// Swap WETH -> BADGER
    function swapWethForBadger(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken == WETH);
        require(orderData.buyToken == BADGER);

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 2.b
    /// Swap WETH -> CVX
    function swapWethForCVX(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken == WETH);
        require(orderData.buyToken == CVX);

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 3 Emit the CVX
    /// Takes all the CVX, takes fee, locks and emits it
    function swapCVXTobveCVXAndEmit() external nonReentrant {
        // Will take all the CVX left,
        // swap it for bveCVX if cheaper, or deposit it directly
        // and then emit it
        require(msg.sender == manager);

        uint256 totalCVX = CVX.balanceOf(address(this));
        require(totalCVX > 0);

        // Get quote from pool
        uint256 fromPurchase = CVX_BVE_CVX_CURVE.get_dy(0, 1, totalCVX);

        // Check math from vault
        // from Vault code shares = (_amount.mul(totalSupply())).div(_pool);
        uint256 fromDeposit = totalCVX * BVE_CVX.totalSupply() / BVE_CVX.balance();

        uint256 ops_fee;
        uint256 toEmit;

        if(fromDeposit > fromPurchase) {
            // Costs less to deposit

            //  ops_fee = int(total / (1 - BADGER_SHARE) * OPS_FEE), adapted to solidity for precision
            ops_fee = totalCVX * OPS_FEE / (MAX_BPS - BADGER_SHARE);

            toEmit = totalCVX - ops_fee;

            CVX.safeApprove(address(BVE_CVX), totalCVX);

            uint256 treasuryPrevBalance = BVE_CVX.balanceOf(TREASURY);
            uint256 badgerTreePrevBalance = BVE_CVX.balanceOf(BADGER_TREE);

            // If we don't swap
            BVE_CVX.depositFor(TREASURY, ops_fee);
            BVE_CVX.depositFor(BADGER_TREE, toEmit);

            // Update vars as we emit event with them
            ops_fee = BVE_CVX.balanceOf(TREASURY) - treasuryPrevBalance;
            toEmit = BVE_CVX.balanceOf(BADGER_TREE) - badgerTreePrevBalance;
        } else {
            // Buy from pool

            CVX.safeApprove(address(CVX_BVE_CVX_CURVE), totalCVX);

            // fromPurchase is calculated in same call so provides no slippage protection
            // but we already calculated it so may as well use that
            uint256 totalBveCVX = CVX_BVE_CVX_CURVE.exchange(0, 1, totalCVX, fromPurchase);

            ops_fee = totalBveCVX * OPS_FEE / (MAX_BPS - BADGER_SHARE);

            toEmit = totalBveCVX - ops_fee;

            IERC20(address(BVE_CVX)).safeTransfer(TREASURY, ops_fee);
            IERC20(address(BVE_CVX)).safeTransfer(BADGER_TREE, toEmit);
        }

        // Unlock Schedule
        uint256 last_end_time = REWARDS_LOGGER.getUnlockSchedulesFor(
            address(BVE_CVX), address(BVE_CVX)
        ).length - 2;
        REWARDS_LOGGER.setUnlockSchedule(
            address(BVE_CVX),
            address(BVE_CVX),
            toEmit,
            last_end_time,
            last_end_time + 14 days,
            14 days
        );

        // Send event
        emit PerformanceFeeGovernance(address(BVE_CVX), ops_fee);
        emit TreeDistribution(address(BVE_CVX), toEmit, block.number, block.timestamp);
    }

    /// @dev
    /// Step 4 Emit the Badger
    function emitBadger() external nonReentrant {
        // Sends Badger to the Tree
        // Updates the emissions schedule accordingly
        // Emits custom event for it
        uint256 toEmit = BADGER.balanceOf(address(this));
        require(toEmit > 0);

        BADGER.safeTransfer(BADGER_TREE, toEmit);

        // Unlock Schedule
        uint256 toEmitToLiqPool = toEmit * LIQ_FEE / BADGER_SHARE;
        uint256 previousEndTime = REWARDS_LOGGER.getUnlockSchedulesFor(
            address(BVE_CVX), address(BADGER)
        ); // need final last element from this tuple (of unknown length)
        REWARDS_LOGGER.setUnlockSchedule(
            address(BVE_CVX),
            address(BADGER),
            toEmitToLiqPool,
            previousEndTime,
            previousEndTime + 14 days,
            14 days
        );
        REWARDS_LOGGER.setUnlockSchedule(
            address(CVX_BVE_CVX_SETT),
            address(BADGER),
            toEmit - toEmitToLiqPool,
            previousEndTime,
            previousEndTime + 14 days,
            14 days
        );

        emit TreeDistribution(address(BADGER), toEmit, block.number, block.timestamp);
    }
}
