# Truebit TRU token simulator

Mint, retire and burn an unlimited amount of TRU tokens and see how it affects the mint/retire price.

Install py-evm and web3

```
pip install -r requirements.txt
```

Configure the web3 provider

```
export WEB3_PROVIDER_URI=http://localhost:8545
export WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/abc123
```

Files

* `evm.py` uses py-evm to configure an Ethereum chain and exposes some helper functions to interact with contracts
* `truebit.py` uses web3 to load the Truebit contract bytecode from the mainnet and exposes helper functions
* `example.py` shows an example how to mint, retire and burn tokens

## Usage

```python
>>> from truebit import init, info, get_state, mint, retire, burn

>>> init(initial_mint=5_000_000, initial_reserve=5)

>>> info()
supply 5000000 TRU
deposits 5 ETH
reserve 5 ETH
mint price 0.0000080000008 ETH
retire price 0.000001 ETH
opex 25000000000000000000000

>>> mint(1000)
>>> info()
supply 5001000 TRU
deposits 5.0080008 ETH
reserve 5.0020002 ETH
mint price 0.0000080016008 ETH
retire price 0.0000010002 ETH
opex 24995000999800039992001

>>> retire(500)
>>> info()
supply 5000500 TRU
deposits 5.0075007 ETH
reserve 5.0015001 ETH
mint price 0.000008001600800079 ETH
retire price 0.0000010002 ETH
opex 24995000999800039992001

>>> burn(500)
>>> info()
supply 5000000 TRU
deposits 5.0075007 ETH
reserve 5.0015001 ETH
mint price 0.00000800240096024 ETH
retire price 0.00000100030002 ETH
opex 24992501749625077484253
```

## `example.py`

```
Running
supply 5000000 TRU
deposits 5 ETH
reserve 5 ETH
mint price 0.0000080000008 ETH
retire price 0.000001 ETH
opex 25000000000000000000000

Minted 1000 TRU...
supply 5001000 TRU
deposits 5.0080008 ETH
reserve 5.0020002 ETH
mint price 0.0000080016008 ETH
retire price 0.0000010002 ETH
opex 24995000999800039992001

Retired 1000 TRU...
supply 5000000 TRU
deposits 5.0070006 ETH
reserve 5.001 ETH
mint price 0.00000800160080016 ETH
retire price 0.0000010002 ETH
opex 24995000999800039992001

Minted 1000 TRU...
supply 5001000 TRU
deposits 5.01500300016 ETH
reserve 5.00300060004 ETH
mint price 0.00000800320112016 ETH
retire price 0.00000100040004 ETH
opex 24990002999200199952011

Burned 1000 TRU...
supply 5000000 TRU
deposits 5.01500300016 ETH
reserve 5.00300060004 ETH
mint price 0.000008004801760544 ETH
retire price 0.000001000600120008 ETH
opex 24985005998000599832044

Minted 275m TRU...
supply 280000000 TRU
deposits 62742.64252750176 ETH
reserve 15689.40988172544 ETH
mint price 0.000448268854564064 ETH
retire price 0.000056033606720448 ETH
opex 446160821392867854143

retire/mint ratio 0.1249999997767857414557450550
```

## Supply vs mint price

```python
mint_amount = 5_000_000
while True:
 state = get_state()
 print('Supply', state["supply"], 'Price', state["mint"], 'ETH')
 mint(mint_amount)
 mint_amount *= 2
 ```

 ```
Supply 5000000 Price 0.0000080000008 ETH
Supply 10000000 Price 0.0000160000008 ETH
Supply 20000000 Price 0.0000320000008 ETH
Supply 40000000 Price 0.0000640000008 ETH
Supply 80000000 Price 0.0001280000008 ETH
Supply 160000000 Price 0.0002560000008 ETH
Supply 320000000 Price 0.0005120000008 ETH
eth.exceptions.Revert: b'... SafeMath: multiplication overflow ...'
 ```