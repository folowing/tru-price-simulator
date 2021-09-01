from secrets import token_bytes

from eth import constants
from eth.chains.base import MiningChain
from eth.consensus.pow import mine_pow_nonce
from eth.db.atomic import AtomicDB
from eth.vm.forks.berlin import BerlinVM

from eth_abi import encode_abi, decode_abi
from eth_keys import keys
from eth_utils import to_wei, from_wei, function_signature_to_4byte_selector


def ether(n, to_unit='ether'):
  return from_wei(n, to_unit)

def wei(n, from_unit='ether'):
  return to_wei(n, from_unit)

def encode_abi_function(name, arguments=None):
  values, types = zip(*arguments) if arguments else ([], [])
  return function_signature_to_4byte_selector(name + '(' + ','.join(types) + ')') + encode_abi(types, values)


class Ethereum:
  def __init__(self, genesis_state=None):
    genesis_params = {
      'parent_hash': constants.GENESIS_PARENT_HASH,
      'uncles_hash': constants.EMPTY_UNCLE_HASH,
      'coinbase': constants.ZERO_ADDRESS,
      'transaction_root': constants.BLANK_ROOT_HASH,
      'receipt_root': constants.BLANK_ROOT_HASH,
      'difficulty': 1,
      'block_number': constants.GENESIS_BLOCK_NUMBER,
      'gas_limit': constants.GAS_LIMIT_MAXIMUM,
      'extra_data': constants.GENESIS_EXTRA_DATA,
      'nonce': constants.GENESIS_NONCE
    }

    self.chain = MiningChain \
                  .configure(vm_configuration=((constants.GENESIS_BLOCK_NUMBER, BerlinVM),)) \
                  .from_genesis(AtomicDB(), genesis_params, genesis_state)

  @property
  def vm(self):
    return self.chain.get_vm()
  
  @property
  def state(self):
    return self.vm.state

  @staticmethod
  def generate_address():
    private_key = keys.PrivateKey(token_bytes(32))
    address = private_key.public_key.to_canonical_address()
    return address, private_key

  def get_balance(self, address, unit='ether'):
    return ether(self.state.get_balance(address), unit)
  
  def mine_block(self):
    block = self.vm.finalize_block(self.chain.get_block()).block

    nonce, mix_hash = mine_pow_nonce(
      block.number, 
      block.header.mining_hash,
      block.header.difficulty)

    self.chain.mine_block(mix_hash=mix_hash, nonce=nonce)
  
  def call(self, sender, address, name, arguments, value=0, gas=1_000_000):
    tx = self.vm \
             .create_unsigned_transaction(
                to=address, 
                data=encode_abi_function(name, arguments),
                value=value,
                nonce=self.state.get_nonce(sender.public_key.to_canonical_address()),
                gas_price=1,
                gas=gas) \
             .as_signed_transaction(sender)
    
    block, receipt, computation = self.chain.apply_transaction(tx)
    computation.raise_if_error()

  def view(self, address, name, arguments, returns):
    tx = self.vm \
             .create_unsigned_transaction(
                to=address,
                data=encode_abi_function(name, arguments),
                value=0,
                nonce=0,
                gas_price=1,
                gas=constants.GAS_LIMIT_MAXIMUM) \
             .as_signed_transaction(keys.PrivateKey(constants.NULL_BYTE * 32))

    result = self.chain.get_transaction_result(tx, self.chain.get_canonical_head())

    if isinstance(returns, str):
      return decode_abi([returns], result)[0]
    else:
      return decode_abi(returns, result)
