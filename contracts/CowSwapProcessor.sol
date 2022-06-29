// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@oz/security/ReentrancyGuard.sol";

import "../libraries/cowswap/CowSwapValidation.sol";

/// @title CowSwapProcessor
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev this is a smart contract that receives swap request from other on-chain callers 
/// @dev and allow off-chain bots to execute CowSwap order upon those requests
/// @notice CREDITS
/// Thank you CowSwap Team as well as Poolpi
/// @notice For the awesome project and the tutorial: https://hackmd.io/@2jvugD4TTLaxyG3oLkPg-g/H14TQ1Omt
contract CowSwapProcessor is ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public manager;
	
    // Contract we will ask for a fair price of before accepting the cowswap order
    address public pricer;		
	
    // Only whitelisted address allowed to request a CowSwap order, typically harvesting strategy
    mapping(address => bool) public validRequesters;
    
    // Only permissioned address allowed to finally submit(by presigning) the CowSwap order request, typically off-chain keeper bots
    mapping(address => bool) public validSubmitters;
	
    /// @dev tracking submitted orders
    mapping(bytes32 => bytes) public requestOrderIds;
	
    mapping(bytes32 => bool) public requestPreSignatures;
	
    /// @dev off-chain bots could read from this mapping for queued requests and then submit them
    mapping(bytes32 => OrderRequest) public requests;
	
    /// @dev queued request(pending submit) count 
    uint256 public queuedRequestCount;
    
    /// @dev maximum allowed pending order requests to be executed
    uint256 public maxRequestInQueue;
	
    event OrderRequested(bytes32 indexed appData, address indexed requester, address tokenIn, address tokenOut, uint256 amountIn, uint256 deadline);
    event OrderSubmitted(bytes32 indexed appData, address indexed requester, address tokenIn, address tokenOut, uint256 amountIn, uint256 expectOutput, uint256 deadline);
    event ManagerSet(address indexed oldManager, address indexed newManager);
    event RequesterSet(address indexed request, bool enable);
    event SubmitterSet(address indexed submitter, bool enable);
	
    struct OrderRequest{
        address requester; // who will receive the output token
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 deadline; // when the order is invalid if not filled successfully		
    }
	
    constructor(address _pricer) {
        manager = msg.sender;
        maxRequestInQueue = 25;
        pricer = _pricer;
        validSubmitters[manager] = true;
    }
	
    // Start permission checks
	
    function _checkManager() internal {
        require(msg.sender == manager, '!MGR');
    }
	
    function _checkRequester() internal {
        require(validRequesters[msg.sender], '!RQT');
    }
	
    function _checkSubmitter() internal {
        require(validSubmitters[msg.sender], '!SUB');
    }
	
    // End permission checks
	
    // Start manager setters

    function setPricer(address _pricer) external {
        _checkManager();
        pricer = _pricer;
    }

    function setManager(address newManager) external {
        _checkManager();
        emit ManagerSet(manager, newManager);
        manager = newManager;
    }

    function setRequesters(address _requester, bool _enable) external {
        _checkManager();
        validRequesters[_requester] = _enable;
        emit RequesterSet(_requester, _enable);
    }

    function setSubmitters(address _submitter, bool _enable) external {
        _checkManager();
        validSubmitters[_submitter] = _enable;
        emit SubmitterSet(_submitter, _enable);
    }

    function setMaxRequestInQueue(uint256 _max) external {
        _checkManager();
        require(_max < 100, '!BIG');
        maxRequestInQueue = _max;
    }
	
    // End manager setters
	
    /// @dev Just in case we need to return funds safely to requester if the order request failed to execute
    function incaseOrderExpired(bytes32 appData) external nonReentrant {
        _checkManager();
		
        // Only if not submitted yet
        bool _presigned = requestPreSignatures[appData];
        require(!_presigned, '!SGN');		
        bytes memory _orderID = requestOrderIds[appData];
        require(_orderID.length <= 0, '!OID');
		
        // Only the deadline has passed already
        OrderRequest memory request = requests[appData];
        require(request.deadline < block.timestamp, '!EXP');
		
        // Update mapping
        require(queuedRequestCount != 0, '!CNT');
        unchecked{
           --queuedRequestCount;
        }
        delete requests[appData];
		
        // Ensure we have enough token to return
        require(IERC20(request.tokenIn).balanceOf(address(this)) >= request.amountIn, '!GON');
        IERC20(request.tokenIn).safeTransfer(request.requester, request.amountIn);
    }
	
    /// @dev Allows whitelisted caller to queue a swap request to be executed by CowSwap 
    /// @notice Caller should approve amountIn of tokenIn in advance to this contract
    /// @return appData and validTo fields for follow-up off-chain order submission
    function requestCowSwapOrder(address tokenIn, address tokenOut, uint256 amountIn) external nonReentrant returns(bytes32,uint256) {
        _checkRequester();
		
        require(queuedRequestCount < maxRequestInQueue, '!MAX');
        require(amountIn != 0, '!ZRO');
		
        // transfer tokenIn from caller
        _safeTransfeFrom(tokenIn, amountIn);
		
        (bytes32 appData, uint256 deadline) = CowSwapValidation.assembleOrderAppData(tokenIn, tokenOut, amountIn);
        requests[appData] = OrderRequest(msg.sender, tokenIn, tokenOut, amountIn, deadline);
		
        unchecked{
           ++queuedRequestCount;
        }
		
        emit OrderRequested(appData, msg.sender, tokenIn, tokenOut, amountIn, deadline);
		
        return (appData, deadline);
    }
		
    /// @dev Allow permissioned caller helping to achieve final submission for given CowSwap order by presigning on-chain
    function submitCowSwapOrder(Data calldata orderData, bytes calldata orderUid) external nonReentrant {
        _checkSubmitter();
		
        bytes32 appData = orderData.appData;

        // Check against stored order request	
        OrderRequest memory request = requests[appData];
        require(request.amountIn != 0, '!NON');// request existence check
        require(request.requester == orderData.receiver, '!REQ');
        require(request.deadline <= uint256(orderData.validTo), '!TTL');
	    
        // Ensure everything looks good before final signing and order submission
        CowSwapValidation.checkCowswapOrder(orderData, orderUid, pricer);
		
        // Update mappings
        requestOrderIds[appData] = orderUid;
        requestPreSignatures[appData] = true;
		
        require(queuedRequestCount != 0, '!CNT');
        unchecked{
           --queuedRequestCount;
        }
		
        // Finalize the order submission
        if(orderData.sellToken.allowance(address(this), CowSwapValidation.RELAYER) <= 0){		 
           orderData.sellToken.safeApprove(CowSwapValidation.RELAYER, type(uint256).max);
        }
        CowSwapValidation._doCowswapOrder(orderUid);
		
        emit OrderSubmitted(appData, request.requester, address(orderData.sellToken), address(orderData.buyToken), request.amountIn, orderData.buyAmount, uint256(orderData.validTo));
    }
	
    // Start view functions
	
    function getOrderID(Data calldata orderData) public view returns (bytes memory) {
        return CowSwapValidation.getOrderID(orderData);
    }
	
    function getPreSignature(bytes calldata orderUid) public view returns (uint256) {
        return CowSwapValidation._settlementSignature(orderUid);
    }
	
    // End view functions
	
    function _safeTransfeFrom(address token, uint256 value) internal {
        uint256 _beforeVal = IERC20(token).balanceOf(address(this));

        (bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transferFrom.selector, msg.sender, address(this), value));
        require(success && (data.length == 0 || abi.decode(data, (bool))), 'STF');

        uint256 _afterVal = IERC20(token).balanceOf(address(this));
        uint256 _diff = _afterVal - _beforeVal;
        require(_diff == value, 'STFdiff');// no support for tokens those charge tax upon transfer
    }
}