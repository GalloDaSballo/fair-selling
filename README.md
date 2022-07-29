# Fair Selling

A BadgerDAO sponsored repo of Open Source Contracts for:
- Integrating Smart Contracts with Cowswap
- Non-Custodial handling of tokens via BribesProcessors
- Calculating onChain Prices
- Executing the best onChain Swap

## Release V0.3 - Pricer - BribesProcessor - CowswapSeller

# Notable Contracts
## CowswapSeller

OnChain Integration with Cowswap, all the functions you want to:
- Verify an Order
- Retrieve the OrderUid from the orderData
- Validate an order through basic security checks (price is correct, sends to correct recipient)
- Integrated with an onChain Pricer (see below), to offer stronger execution guarantees

## BribesProcessor

Anti-rug technplogy, allows a Multi-sig to rapidly process CowSwap orders, without allowing the Multi to rug
Allows tokens to be rescued without the need for governance via the `ragequit` function

- `AuraBribesProcessor` -> Processor for Votium Bribes earned by `bveAura`
- `VotiumBribesProcessor` -> Processor for Votium Bribes earned by `bveCVX`

## OnChainPricingMainnet

Given a tokenIn, tokenOut and AmountIn, returns a Quote from the most popular dexes

- `OnChainPricingMainnet` -> Fully onChain math to find best, single source swap (no fragmented swaps yet)
- `OnChainPricingMainnetLenient` -> Slippage tollerant version of the Pricer

### Dexes Support
- Curve
- UniV2
- UniV3
- Balancer
- Sushi

Covering >80% TVL on Mainnet. (Prob even more)

# Ar



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



# Notable Tests

## Benchmark specific AMM quotes
TODO: Improve to just use the specific quote

```
brownie test tests/gas_benchmark/benchmark_pricer_gas.py --gas
```

## Benchmark coverage of top DeFi Tokens

TODO: Add like 200 tokens
TODO: Compare against Coingecko API or smth

```
brownie test tests/gas_benchmark/benchmark_token_coverage.py --gas
```

## Notable Test from V2

Run V3 Pricer against V2, to confirm results are correct, but with gas savings

```
brownie test  tests/heuristic_equivalency/test_heuristic_equivalency.py
```