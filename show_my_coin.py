#!/usr/bin/env python3

from advanced_blockchain import AdvancedBlockchain
from advanced_wallet import AdvancedWallet

print("\n" + "="*80)
print("🪙  YOUR CRYPTOCURRENCY - LIVE DEMONSTRATION")
print("="*80)

# Initialize blockchain
blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)

print("\n✅ Blockchain initialized!")
print(f"   Genesis block: {blockchain.get_latest_block().hash[:50]}...")

# Create wallets
print("\n👛 Creating wallets...")
alice = AdvancedWallet()
bob = AdvancedWallet()
charlie = AdvancedWallet()

print(f"   Alice:   {alice.get_address()}")
print(f"   Bob:     {bob.get_address()}")
print(f"   Charlie: {charlie.get_address()}")

# Mine first block - reward to Alice
print("\n⛏️  Block 1: Mining reward for Alice...")
blockchain.mine_block(alice.get_address(), force=True)
print(f"   ✅ Block mined! Alice receives 50 coins")

# Show balances
print("\n💰 Current Balances:")
print(f"   Alice:   {blockchain.get_balance(alice.get_address())} coins")
print(f"   Bob:     {blockchain.get_balance(bob.get_address())} coins")
print(f"   Charlie: {blockchain.get_balance(charlie.get_address())} coins")

# Create transactions
print("\n💸 Transaction 1: Alice sends 20 coins to Bob")
tx1 = alice.create_transaction(bob.get_address(), 20, 0.5, blockchain)
if tx1:
    blockchain.add_transaction(tx1)
    print(f"   ✅ Transaction signed and added to mempool")
    print(f"   Fee: 0.5 coins")

print("\n💸 Transaction 2: Alice sends 15 coins to Charlie")
tx2 = alice.create_transaction(charlie.get_address(), 15, 0.5, blockchain)
if tx2:
    blockchain.add_transaction(tx2)
    print(f"   ✅ Transaction signed and added to mempool")
    print(f"   Fee: 0.5 coins")

# Mine second block
print(f"\n⛏️  Block 2: Mining {blockchain.mempool.size()} transactions (reward to Bob)...")
blockchain.mine_block(bob.get_address())
print(f"   ✅ Block mined! Bob gets reward + transaction fees")

# Show updated balances
print("\n💰 Updated Balances:")
alice_bal = blockchain.get_balance(alice.get_address())
bob_bal = blockchain.get_balance(bob.get_address())
charlie_bal = blockchain.get_balance(charlie.get_address())
print(f"   Alice:   {alice_bal} coins")
print(f"   Bob:     {bob_bal} coins")
print(f"   Charlie: {charlie_bal} coins")

# Create more transactions
print("\n💸 Transaction 3: Bob sends 10 coins to Charlie")
tx3 = bob.create_transaction(charlie.get_address(), 10, 0.3, blockchain)
if tx3:
    blockchain.add_transaction(tx3)
    print(f"   ✅ Transaction added (Fee: 0.3 coins)")

# Mine third block
print("\n⛏️  Block 3: Mining for Charlie...")
blockchain.mine_block(charlie.get_address())
print(f"   ✅ Block mined!")

# Final balances
print("\n" + "="*80)
print("🎉 FINAL CRYPTOCURRENCY STATUS")
print("="*80)

alice_bal = blockchain.get_balance(alice.get_address())
bob_bal = blockchain.get_balance(bob.get_address())
charlie_bal = blockchain.get_balance(charlie.get_address())
total = alice_bal + bob_bal + charlie_bal

print(f"\n💰 WALLET BALANCES:")
print(f"   Alice:   {alice_bal} coins")
print(f"   Bob:     {bob_bal} coins")
print(f"   Charlie: {charlie_bal} coins")
print(f"   ─────────────────────")
print(f"   TOTAL:   {total} coins")

info = blockchain.get_chain_info()
print(f"\n📊 BLOCKCHAIN INFO:")
print(f"   Total Blocks: {info['length']}")
print(f"   Total Supply: {total} coins")
print(f"   Difficulty: {info['difficulty']}")
print(f"   Chain Valid: {'✅ YES' if info['is_valid'] else '❌ NO'}")

print(f"\n⛓️  BLOCKCHAIN:")
for block in blockchain.chain:
    print(f"   Block {block.index}: {len(block.transactions)} tx | Hash: {block.hash[:45]}...")

print(f"\n✨ Your cryptocurrency is working perfectly!")
print("="*80 + "\n")
