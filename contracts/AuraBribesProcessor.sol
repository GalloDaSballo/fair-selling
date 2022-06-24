// SPDX-License-Identifier: MIT
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
    event AuraDepositAmount(uint256 amount);
    event AuraSwapAmount(uint256 amount);

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

    uint256 public constant MAX_BPS = 10_000;
    uint256 public constant BADGER_SHARE = 2750; //27.50%
    uint256 public constant OPS_FEE = 500; // 5%
    uint256 public constant LP_FEE = 500; // 5%

    /// `treasury_vault_multisig`
    /// https://github.com/Badger-Finance/badger-multisig/blob/9f04e0589b31597390f2115501462794baca2d4b/helpers/addresses.py#L38
    address public constant TREASURY = 0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e;

    IVault public constant BVE_AURA = IVault(0xBA485b556399123261a5F9c95d413B4f93107407);

    bytes32 public constant AURA_BVEAURA_POOL_ID = 0x9f40f06ea32304dc777ecc661609fb6b0c5daf4a00020000000000000000026a;

    IBalancerVault public constant BALANCER_VAULT = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);


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
        require(orderData.sellToken == WETH);
        require(orderData.buyToken == BADGER);

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 2.b
    /// Swap WETH -> AURA
    function swapWethForAURA(Data calldata orderData, bytes memory orderUid) external {
        require(orderData.sellToken == WETH);
        require(orderData.buyToken == AURA);

        /// NOTE: checks for msg.sender == manager
        _doCowswapOrder(orderData, orderUid);
    }

    /// @dev
    /// Step 3 Emit the Aura
    /// Takes all the Aura, takes fee, locks and emits it
    function swapAURATobveAURAAndEmit() external nonReentrant {
        // Will take all the Aura left,
        // swap it for bveAura if cheaper, or deposit it directly
        // and then emit it
        require(msg.sender == manager);

        uint256 totalAURA = AURA.balanceOf(address(this));
        require(totalAURA > 0);
        require(HARVEST_FORWARDER.badger_tree() == BADGER_TREE);

        // Get quote from balancer pool using queryBatchSwap

        IBalancerVault.FundManagement memory fundManagement = IBalancerVault.FundManagement({
            sender: address(this),
            fromInternalBalance: false,
            recipient: payable(address(this)),
            toInternalBalance: false
        });

        IAsset[] memory assets = new IAsset[](2);
        assets[0] = IAsset(address(AURA));
        assets[1] = IAsset(address(BVE_AURA));

        IBalancerVault.BatchSwapStep memory batchSwapStep = IBalancerVault.BatchSwapStep({
            poolId: AURA_BVEAURA_POOL_ID,
            assetInIndex: 0,
            assetOutIndex: 1,
            amount: totalAURA,
            userData: new bytes(0)
        });

        IBalancerVault.BatchSwapStep[] memory swaps = new IBalancerVault.BatchSwapStep[](1);
        swaps[0] = batchSwapStep;
        
        int256 fromPurchase = BALANCER_VAULT.queryBatchSwap(
            IBalancerVault.SwapKind.GIVEN_IN,
            swaps,
            assets,
            fundManagement
        )[0];

        // Check math from vault
        // from Vault code shares = (_amount.mul(totalSupply())).div(_pool);
        uint256 fromDeposit = totalAURA * BVE_AURA.totalSupply() / BVE_AURA.balance();

        emit AuraDepositAmount(fromDeposit);
        emit AuraSwapAmount(uint256(fromPurchase));

        uint256 ops_fee;
        uint256 toEmit;

        if(fromDeposit > uint256(fromPurchase)) {
            // Costs less to deposit

            //  ops_fee = int(total / (1 - BADGER_SHARE) * OPS_FEE), adapted to solidity for precision
            ops_fee = totalAURA * OPS_FEE / (MAX_BPS - BADGER_SHARE);

            toEmit = totalAURA - ops_fee;
            AURA.safeApprove(address(BVE_AURA), totalAURA);
            uint256 treasuryPrevBalance = BVE_AURA.balanceOf(TREASURY);

            // If we don't swap

            // Take the fee
            BVE_AURA.depositFor(TREASURY, ops_fee);

            // Deposit and emit rest
            uint256 initialBveAURABalance = BVE_AURA.balanceOf((address(this)));
            BVE_AURA.deposit(toEmit);

            // Update vars as we emit event with them
            ops_fee = BVE_AURA.balanceOf(TREASURY) - treasuryPrevBalance;
            toEmit = BVE_AURA.balanceOf(address(this)) - initialBveAURABalance;
        } else {
            // Buy from pool using singleSwap

            AURA.safeApprove(address(BALANCER_VAULT), totalAURA);

            IBalancerVault.SingleSwap memory singleSwap = IBalancerVault.SingleSwap({
                poolId: AURA_BVEAURA_POOL_ID,
                kind: IBalancerVault.SwapKind.GIVEN_IN,
                assetIn: IAsset(address(AURA)),
                assetOut: IAsset(address(BVE_AURA)),
                amount: totalAURA,
                userData: new bytes(0)
            });

            uint256 totalBveAURA = BALANCER_VAULT.swap(singleSwap, fundManagement, 0, type(uint256).max);

            ops_fee = totalBveAURA * OPS_FEE / (MAX_BPS - BADGER_SHARE);

            toEmit = totalBveAURA - ops_fee;

            // Take fee
            IERC20(address(BVE_AURA)).safeTransfer(TREASURY, ops_fee);
        }

        // Emit token
        IERC20(address(BVE_AURA)).safeApprove(address(HARVEST_FORWARDER), toEmit);
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
        uint256 toEmitTotal = BADGER.balanceOf(address(this));
        require(toEmitTotal > 0);

        BADGER.safeApprove(address(HARVEST_FORWARDER), toEmitTotal);
        HARVEST_FORWARDER.distribute(address(BADGER), toEmitTotal, address(BVE_AURA));

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
