from evm import Ethereum, wei, ether
from web3.auto import w3


# TRU token contract https://etherscan.io/address/0xf65B5C5104c4faFD4b709d9D60a185eAE063276c
# Purchase contract for minting, retiring https://etherscan.io/address/0x764C64b2A09b09Acb100B80d8c505Aa6a0302EF2
# these are upgradable proxy contracts
# you can find the value for the IMPLEMENTATION_SLOT variable in the code on etherscan.io under Contract
trutoken_address = w3.eth.get_storage_at("0xf65B5C5104c4faFD4b709d9D60a185eAE063276c", "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")[12:]
purchase_address = w3.eth.get_storage_at("0x764C64b2A09b09Acb100B80d8c505Aa6a0302EF2", "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")[12:]

deployer_address, deployer = Ethereum.generate_address()

eth = Ethereum({
  deployer_address: {
    "balance": wei(1_000_000_000),
    "nonce": 0,
    "code": b'',
    "storage": {}
  },
  trutoken_address: {
    "balance": 0,
    "nonce": 0,
    "code": w3.eth.get_code(trutoken_address),
    "storage": {}
  },
  purchase_address: {
    "balance": 0,
    "nonce": 0,
    "code": w3.eth.get_code(purchase_address),
    "storage": {}
  }
})


def init(initial_mint, initial_reserve):
  # https://etherscan.io/tx/0x8c710b241c6b4ab10a590d84dbb6d03331f9f33969638dfe140dbff9f74cd73f
  eth.call(deployer, trutoken_address, 'initialize', [('Truebit', 'string'), ('TRU', 'string')])
  # https://etherscan.io/tx/0xde47b1f63be20dd44eb3b9da692c85bc14a25cb63e77bf80de561f39662e05b5
  eth.call(deployer, trutoken_address, 'mint', [(deployer_address, 'address'), (wei(initial_mint), 'uint256')])
  # https://etherscan.io/tx/0xa180429fe51eff4f42bb4371911657ed059b4d32f468272bf094e44de4fe556c
  eth.call(deployer, trutoken_address, 'grantRole', [(bytes.fromhex('9f2df0fed2c77648de5860a4cc508cd0818c85b8b8a1ab4ceeef8d981c8956a6'), 'bytes32'), (purchase_address, 'address')])

  # https://etherscan.io/tx/0xed2b012661565010c90b2133afc9abdc87f3d5af6d7d37d86f0921713a4ade35
  eth.call(deployer, purchase_address, 'initialize', [(trutoken_address, 'address'), (deployer_address, 'address')])
  # https://etherscan.io/tx/0xb23b8d7a12b978ba8c217cfe70c6ce7e5bc422374252f7ffacf3f31da79da30b
  eth.call(deployer, purchase_address, 'donateToReserve', [], value=wei(initial_reserve))

  eth.call(deployer, trutoken_address, 'increaseAllowance', [(purchase_address, 'address'), (wei(1_000_000_000), 'uint256')])
  eth.mine_block()

def mint(n):
  cost = eth.view(purchase_address, 'getPurchasePrice', [(wei(n), 'uint256')], returns='uint256')
  eth.call(deployer, purchase_address, 'buyTRU', [(wei(n), 'uint256')], value=cost)
  eth.mine_block()

def retire(n):
  eth.call(deployer, purchase_address, 'sellTRU', [(wei(n), 'uint256')])
  eth.mine_block()

def burn(n):
  eth.call(deployer, trutoken_address, 'burn', [(wei(n), 'uint256')])
  eth.mine_block()

def get_state():
  return {
    "supply": ether(eth.view(trutoken_address, 'totalSupply', [], returns='uint256')),
    "deposits": ether(eth.get_balance(purchase_address, 'wei')),
    "reserve": ether(eth.view(purchase_address, 'reserve', [], returns='uint256')),
    "mint": ether(eth.view(purchase_address, 'getPurchasePrice', [(wei(1), 'uint256')], returns='uint256')),
    "retire": ether(eth.view(purchase_address, 'getRetirePrice', [(wei(1), 'uint256')], returns='uint256')),
    # no idea what these are but they are in the ABI
    "opex": eth.view(purchase_address, 'opex', [], returns='uint256'),
    "opex_cost": eth.view(purchase_address, 'OPEX_COST', [], returns='uint256'),
    "theta": eth.view(purchase_address, 'THETA', [], returns='uint256')
  }

def info():
  state = get_state() 

  print('supply', state["supply"], 'TRU')
  print('deposits', state["deposits"], 'ETH')
  print('reserve', state["reserve"], 'ETH')
  print('mint price', state["mint"], 'ETH')
  print('retire price', state["retire"], 'ETH')
  print()
