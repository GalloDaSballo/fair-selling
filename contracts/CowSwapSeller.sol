// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;


import {IERC20} from "@oz/token/ERC20/IERC20.sol";
import {SafeERC20} from "@oz/token/ERC20/utils/SafeERC20.sol";


import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/curve/ICurveRouter.sol";

// Onchain Pricing Interface
struct Quote {
    string name;
    uint256 amountOut;
}
interface OnChainPricing {
  function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external returns (Quote memory);
}
// END OnchainPricing

/// @title CowSwapSeller
/// @author Alex the Entreprenerd @ BadgerDAO
/// @dev Cowswap seller, a smart contract that receives order data and verifies if the order is worth going for
/// @notice CREDIS
/// Thank you Cowswap Team as well as Poolpi
/// @notice For the awesome project and the tutorial: https://hackmd.io/@2jvugD4TTLaxyG3oLkPg-g/H14TQ1Omt
contract CowSwapSeller {
  OnChainPricing pricer; // Contract we will ask for a fair price of before accepting the cowswap order

  address manager;

  bytes32 private constant TYPE_HASH =
        hex"d5a25ba2e97094ad7d83dc28a6572da797d6b3e7fc6663bd93efb789fc17e489";

    // keccak256("sell")
    bytes32 public constant KIND_SELL =
        hex"f3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775";
    // keccak256("erc20")
    bytes32 public constant BALANCE_ERC20 =
        hex"5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9";

  /// @dev The domain separator used for signing orders that gets mixed in
  /// making signatures for different domains incompatible. This domain
  /// separator is computed following the EIP-712 standard and has replay
  /// protection mixed in so that signed orders are only valid for specific
  /// GPv2 contracts.
  /// @notice Copy pasted from mainnet because we need this
  bytes32 public constant domainSeparator = 0xc078f884a2676e1345748b1feace7b0abee5d00ecadb6e574dcdd109a63e8943;
    // Cowswap Order Data Interface 
  uint256 constant UID_LENGTH = 56;

  struct Data {
      IERC20 sellToken;
      IERC20 buyToken;
      address receiver;
      uint256 sellAmount;
      uint256 buyAmount;
      uint32 validTo;
      bytes32 appData;
      uint256 feeAmount;
      bytes32 kind;
      bool partiallyFillable;
      bytes32 sellTokenBalance;
      bytes32 buyTokenBalance;
  }
    

  /// @dev Packs order UID parameters into the specified memory location. The
  /// result is equivalent to `abi.encodePacked(...)` with the difference that
  /// it allows re-using the memory for packing the order UID.
  ///
  /// This function reverts if the order UID buffer is not the correct size.
  ///
  /// @param orderUid The buffer pack the order UID parameters into.
  /// @param orderDigest The EIP-712 struct digest derived from the order
  /// parameters.
  /// @param owner The address of the user who owns this order.
  /// @param validTo The epoch time at which the order will stop being valid.
  function packOrderUidParams(
      bytes memory orderUid,
      bytes32 orderDigest,
      address owner,
      uint32 validTo
  ) pure public {
      require(orderUid.length == UID_LENGTH, "GPv2: uid buffer overflow");

      // NOTE: Write the order UID to the allocated memory buffer. The order
      // parameters are written to memory in **reverse order** as memory
      // operations write 32-bytes at a time and we want to use a packed
      // encoding. This means, for example, that after writing the value of
      // `owner` to bytes `20:52`, writing the `orderDigest` to bytes `0:32`
      // will **overwrite** bytes `20:32`. This is desirable as addresses are
      // only 20 bytes and `20:32` should be `0`s:
      //
      //        |           1111111111222222222233333333334444444444555555
      //   byte | 01234567890123456789012345678901234567890123456789012345
      // -------+---------------------------------------------------------
      //  field | [.........orderDigest..........][......owner.......][vT]
      // -------+---------------------------------------------------------
      // mstore |                         [000000000000000000000000000.vT]
      //        |                     [00000000000.......owner.......]
      //        | [.........orderDigest..........]
      //
      // Additionally, since Solidity `bytes memory` are length prefixed,
      // 32 needs to be added to all the offsets.
      //
      // solhint-disable-next-line no-inline-assembly
      assembly {
          mstore(add(orderUid, 56), validTo)
          mstore(add(orderUid, 52), owner)
          mstore(add(orderUid, 32), orderDigest)
      }
    }
    constructor(OnChainPricing _pricer) {
        pricer = _pricer;
        manager = msg.sender;
    }

    function setManager(address newManager) external {
        require(msg.sender == manager);
        manager = newManager;
    }



    function initiateCowswapOrder() external {
        require(msg.sender == manager);

        // TODO: Verify data, verify quote, if valid setPresignature
    }

    function stringToBytes32(string memory source) public pure returns (bytes32 result) {
        return bytes32(bytes(source));
    }

    /// @dev Return the EIP-712 signing hash for the specified order.
    ///
    /// @param order The order to compute the EIP-712 signing hash for.
    /// @param separator The EIP-712 domain separator to use.
    /// @return orderDigest The 32 byte EIP-712 struct hash.
    function getHash(Data memory order, bytes32 separator)
        public
        pure
        returns (bytes32 orderDigest)
    {
        bytes32 structHash;

        // NOTE: Compute the EIP-712 order struct hash in place. As suggested
        // in the EIP proposal, noting that the order struct has 10 fields, and
        // including the type hash `(12 + 1) * 32 = 416` bytes to hash.
        // <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md#rationale-for-encodedata>
        // solhint-disable-next-line no-inline-assembly
        assembly {
            let dataStart := sub(order, 32)
            let temp := mload(dataStart)
            mstore(dataStart, TYPE_HASH)
            structHash := keccak256(dataStart, 416)
            mstore(dataStart, temp)
        }

        // NOTE: Now that we have the struct hash, compute the EIP-712 signing
        // hash using scratch memory past the free memory pointer. The signing
        // hash is computed from `"\x19\x01" || domainSeparator || structHash`.
        // <https://docs.soliditylang.org/en/v0.7.6/internals/layout_in_memory.html#layout-in-memory>
        // <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md#specification>
        // solhint-disable-next-line no-inline-assembly
        assembly {
            let freeMemoryPointer := mload(0x40)
            mstore(freeMemoryPointer, "\x19\x01")
            mstore(add(freeMemoryPointer, 2), separator)
            mstore(add(freeMemoryPointer, 34), structHash)
            orderDigest := keccak256(freeMemoryPointer, 66)
        }
    }

    function getOrderID(Data calldata orderData) public view returns (bytes memory) {
        // Allocated
        bytes memory orderUid = new bytes(UID_LENGTH);

        // Get the hash
        bytes32 digest = getHash(orderData, domainSeparator);
        packOrderUidParams(orderUid, digest, address(this), orderData.validTo);

        return orderUid;
    }
}