from truebit import init, info, get_state, mint, retire, burn

print('Running')
init(initial_mint=5_000_000, initial_reserve=5)
info()

print('Minted 1000 TRU...')
mint(1000)
info()

print('Retired 1000 TRU...')
retire(1000)
info()

print('Minted 1000 TRU...')
mint(1000)
info()

print('Burned 1000 TRU...')
burn(1000)
info()

print('Minted 275m TRU...')
mint(275_000_000)
info()

state = get_state()
print("retire/mint ratio", state["retire"]/state["mint"])
print(state)
