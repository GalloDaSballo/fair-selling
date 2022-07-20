# Fair Selling

## Release V0.2 - Pricer - BribesProcessor - CowswapSeller

# CoswapSeller

OnChain Integration with Cowswap, all the functions you want to:
- Verify an Order
- Retrieve the OrderUid from the orderData
- Validate an order through basic security checks (price is correct, sends to correct recipient)
- Integrated with an onChain Pricer (see below), to offer stronger execution guarantees

# BribesProcessor

Anti-rug technlogy, allows a Multi-sig to rapidly process cowswap orders, without allowing the Multi to rug
Allows tokens to be rescued without the need for governance via the `ragequit` function

# MainnetPricing

Given a tokenIn, tokenOut and AmountIn, returns a Quote from the most popular dexes

## Dexes Support
- Curve
- UniV2
- UniV3
- Balancer
- Sushi

Covering >80% TVL on Mainnet.

## Example Usage

BREAKING CHANGE: V3 is back to `view` even for Balancer and UniV3 functions

### isPairSupported

Returns true if the pricer will return a non-zero quote
NOTE: This is not proof of optimality

```solidity
    /// @dev Given tokenIn, out and amountIn, returns true if a quote will be non-zero
    /// @notice Doesn't guarantee optimality, just non-zero
    function isPairSupported(address tokenIn, address tokenOut, uint256 amountIn) external returns (bool)
```

In Brownie
```python
quote = pricer.isPairSupported(t_in, t_out, amt_in)
```

### findOptimalSwap

Returns the best quote given the various Dexes, used Heuristics to save gas (V0.3 will focus on this)
NOTE: While the function says optimal, this is not optimal, just best of the bunch, optimality may never be achieved fully on-chain

```solidity
    function findOptimalSwap(address tokenIn, address tokenOut, uint256 amountIn) external virtual returns (Quote memory)
```

In Brownie
```python
quote = pricer.findOptimalSwap(t_in, t_out, amt_in)
```


# Mainnet Pricing Lenient

Variation of Pricer with a slippage tollerance

