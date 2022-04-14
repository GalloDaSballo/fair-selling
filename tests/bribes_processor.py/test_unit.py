"""
  Unit tests for all functions
  
  Ragequit
    Anytime from manager
    After 28 days from anyone

  sellBribeForWeth
    Can't sell badger
    Can't sell CVX
    Works for only X to ETH

  swapWethForBadger
    Works
    Reverts if not weth -> badger
  
  swapWethForCVX
    Works
    Reverts if not weth -> CVX
    
  swapCVXTobveCVXAndEmit
    Works for both LP and Buy
    Emits event

  emitBadger
    Works
    Emits event
"""