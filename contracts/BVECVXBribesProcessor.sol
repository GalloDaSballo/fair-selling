// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {CowSwapSeller} from "./CowSwapSeller.sol";
import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


/// @title BribesProcessor
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev BribesProcess for bveCVX, using CowSwapSeller allows to process bribes fairly
/// Minimizing the amount of power that the manager can have
/// @notice This code is WIP, any feedback is appreciated alex@badger.finance
contract BVECVXBribesProcessor is CowSwapSeller {
    using SafeERC20 for IERC20;


    // All events are token / amount
    // TODO: Ask Jintao if it helps or if we can remove extra address
    event SentBribeToTree(address indexed token, uint256 amount);
    event SentBadgerToTree(address indexed token, uint256 amount);
    event SentBadgerLiquidityFeeToTree(address indexed token, uint256 amount);
    event SentCVXFeeToTreasury(address indexed token, uint256 amount);

    // TODO: Bring the following script to onChain
    // https://github.com/Badger-Finance/badger-multisig/blob/main/scripts/badger/swap_bribes_for_bvecvx.py

    // address public manager /// inherited by CowSwapSeller

    // timestamp of last action, we allow anyone to sweep this contract
    // if admin has been idle for too long.
    // Sweeping simply emits to the badgerTree making fair emission to vault depositors
    // Once BadgerRewards is live we will integrate it
    uint256 public lastManagerAction;

    uint256 public constant MAX_MANAGER_IDLE_TIME = 1209600; // 2 Weeks 604800 is 1 week

    IERC20 public constant BADGER = IERC20(0x3472A5A71965499acd81997a54BBA8D852C6E53d);
    IERC20 public constant CVX = IERC20(0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B);

    address public constant BADGER_TREE = 0x660802Fc641b154aBA66a62137e71f331B6d787A;

    uint256 public constant MAX_BPS = 10_000;
    uint256 public constant CVX_FEE_TO_TREASURY = 500; // 5%
    uint256 public constant BADGER_FEE = 500; // 5% // This is actually emitted to tree via custom event
    uint256 public constant TO_SWAP_TO_BADGER = 2125; // 21.25%;

    /// `treasury_vault_multisig`
    /// https://github.com/Badger-Finance/badger-multisig/blob/9f04e0589b31597390f2115501462794baca2d4b/helpers/addresses.py#L38
    address public constant TREASURY = 0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e;

    uint256 totalCVX; // Total amount of CVX we got from swaps
    uint256 toSendAsCVX; // The amount we need to process as CVX
    uint256 cvxForTreasury; // CVX to lock into bveCVX and send to Treasury as fee
    uint256 cvxToBadgerFee; // Cvx to sell for Badger (Fee part)
    uint256 cvxToBadgerToEmit; // Cvx to sell for Badger (to emit to badgerTree)

    constructor(address _pricer) CowSwapSeller(_pricer) {
        lastManagerAction = block.timestamp;
    }


    /// === Security Function === ///

    /// @dev Emits all tokens directly to tree for people to receive
    /// @notice has built in expiration allowing anyone to send the tokens to tree should the manager stop processing bribes
    /// This is effectively a security rescue function
    /// The manager can call it to move funds to tree (forfeiting any fees)
    /// And anyone can rescue the funds if the manager goes rogue
    function sendToTree(IERC20 token) external nonReentrant {
        require(msg.sender == manager || block.timestamp > lastManagerAction + MAX_MANAGER_IDLE_TIME);

        // TODO: In order to avoid selling after, set back the allowance to 0
        token.safeApprove(address(SETTLEMENT), 0);

        // Send all tokens to badgerTree
        uint256 amount = token.balanceOf(address(this));
        token.safeTransfer(BADGER_TREE, amount);

        // Emit Emission Event
        emit SentBribeToTree(address(token), amount);
    }

    /// === Day to Day Operations Functions === ///

    /// Step 0
    /// Setup a new Round
    function startNewRound() external {
        require(msg.sender == manager);
        require(CVX.balanceOf(address(this)) == 0);
        require(BADGER.balanceOf(address(this)) == 0);

        // Resets the balances of CVX for math purposes
        totalCVX = 0;
        cvxForTreasury = 0;
        cvxToBadgerFee = 0;
        cvxToBadgerToEmit = 0;
        // NOTE: May be best to leave as 1 wei as it saves gas


        // Reset the time left before anyone can sweep
        lastManagerAction = block.timestamp;
    }

    /// Step 1 
    /// Use sellBribeForCvx
    /// To sell all bribes to CVX
    /// @notice nonReentrant not needed as `_doCowswapOrder` is nonReentrant
    function sellBribeForCvx(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken != CVX); // Can't sell CVX;
        require(orderData.buyToken == CVX); // Gotta Buy CVX;

        _doCowswapOrder(orderData, orderUid);
    }


    /// Step 2
    /// Once done selling bribs, mark the CVX for Fee Calculation
    function markCVXForThisRound() external {
        require(msg.sender == manager);

        // Set CVX to be equal to the amount we got
        // This allows us to know what needs to be sent as fees vs emitted
        uint256 totalBalance = CVX.balanceOf(address(this));

        require(totalBalance > 0);
        require(totalCVX == 0); // Can't set it again

        // toBadger;
        // asFee;

        uint256 forTeasury = totalBalance * CVX_FEE_TO_TREASURY / MAX_BPS;
        uint256 forBadgerFee = totalBalance * BADGER_FEE / MAX_BPS;
        uint256 toEmitAsBadger = totalBalance * TO_SWAP_TO_BADGER / MAX_BPS;
        totalCVX = totalBalance;
        cvxForTreasury = forTeasury;
        cvxToBadgerFee = forBadgerFee;
        cvxToBadgerToEmit = toEmitAsBadger;

        toSendAsCVX = totalBalance - forTeasury - forBadgerFee - toEmitAsBadger;

        lastManagerAction = block.timestamp;
    }

    /// Step 3 Emit the CVX
    function swapCVXTobveCVXAndEmit() external {
        // Will take all the CVX left, 
        // swap it for bveCVX if cheaper, or deposit it directly 
        // and then emit it
        require(msg.sender == manager);

        // Total to move
        uint256 toMove = toSendAsCVX;
        uint256 forTreasury = cvxForTreasury;

        // Send to Tree toMove
        // Send to Treasury the cvxForTreasury

        // Because CVX / bveCVX is an onChain Pool, we either swap or wrap, fully onChain here
        // No need for cowswap quote

        lastManagerAction = block.timestamp;
    }

    
    /// Step 4 Swap the remaining amount to Badger so you can Emit it
    function setupBadgerSwap(Data calldata orderData, bytes memory orderUid) external {
        // require(msg.sender == manager); // We already check in `_doCowswapOrder`

        require(orderData.sellToken == CVX); // Can only sell CVX (see above);
        require(orderData.buyToken == BADGER); // Gotta Buy BADGER;

        uint256 toEmitAsFee = cvxToBadgerFee;
        uint256 toEmitToDepositors = cvxToBadgerToEmit;

        // We need to be selling the whole amount so we got zero CVX left after this operation
        require(orderData.feeAmount + orderData.sellAmount == toEmitAsFee + toEmitToDepositors);

        _doCowswapOrder(orderData, orderUid);



        lastManagerAction = block.timestamp; // Prob can't let this reset as this could be noop
    }

    /// Step 5 Emit the Badger
    function emitBadger() external {
        // Sends Badger to the Tree
        // Emits custom event for it
        // Take 5% Fee
    }


    // Round is closed now, so manager can start again from step 0


}

