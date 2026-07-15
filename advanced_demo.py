import time
from advanced_blockchain import AdvancedBlockchain
from advanced_wallet import AdvancedWallet
from database import Database


def print_separator():
    print("\n" + "=" * 80 + "\n")


def main():
    print_separator()
    print("ADVANCED CRYPTOCURRENCY SYSTEM DEMO")
    print("Features: ECDSA Signatures, UTXO Model, Mempool, Merkle Trees, SQLite Persistence")
    print_separator()

    print("Initializing blockchain with difficulty=2 and block reward=50 coins...")
    blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)
    database = Database("demo_blockchain.db")

    print(f"Genesis block created: {blockchain.get_latest_block().hash}")
    print_separator()

    print("Creating 3 wallets with ECDSA key pairs...")
    wallet1 = AdvancedWallet()
    wallet2 = AdvancedWallet()
    wallet3 = AdvancedWallet()

    print(f"\nWallet 1:")
    print(f"  Address: {wallet1.get_address()}")
    print(f"  Balance: {blockchain.get_balance(wallet1.get_address())} coins")

    print(f"\nWallet 2:")
    print(f"  Address: {wallet2.get_address()}")
    print(f"  Balance: {blockchain.get_balance(wallet2.get_address())} coins")

    print(f"\nWallet 3:")
    print(f"  Address: {wallet3.get_address()}")
    print(f"  Balance: {blockchain.get_balance(wallet3.get_address())} coins")

    print_separator()
    print("MINING BLOCK 1 - Rewarding Wallet 1")
    print_separator()

    block1 = blockchain.mine_block(wallet1.get_address(), force=True)
    if block1:
        database.save_block(block1)
        print(f"\nBlock 1 Details:")
        print(f"  Hash: {block1.hash}")
        print(f"  Merkle Root: {block1.merkle_root}")
        print(f"  Transactions: {len(block1.transactions)}")
        print(f"\nWallet 1 Balance: {blockchain.get_balance(wallet1.get_address())} coins")

    print_separator()
    print("CREATING TRANSACTIONS WITH SIGNATURES")
    print_separator()

    print("\nTransaction 1: Wallet 1 → Wallet 2 (30 coins, 0.5 fee)")
    tx1 = wallet1.create_transaction(wallet2.get_address(), 30, 0.5, blockchain)
    if tx1:
        blockchain.add_transaction(tx1)
        print(f"  Transaction ID: {tx1.tx_id}")
        print(f"  Signed with ECDSA private key")

    print("\nTransaction 2: Wallet 1 → Wallet 3 (15 coins, 0.5 fee)")
    tx2 = wallet1.create_transaction(wallet3.get_address(), 15, 0.5, blockchain)
    if tx2:
        blockchain.add_transaction(tx2)
        print(f"  Transaction ID: {tx2.tx_id}")

    print(f"\nMempool size: {blockchain.mempool.size()} transactions")

    print_separator()
    print("MINING BLOCK 2 - Including Mempool Transactions")
    print_separator()

    block2 = blockchain.mine_block(wallet2.get_address())
    if block2:
        database.save_block(block2)
        print(f"\nBlock 2 Details:")
        print(f"  Hash: {block2.hash}")
        print(f"  Merkle Root: {block2.merkle_root}")
        print(f"  Transactions: {len(block2.transactions)}")
        print(f"  Total Fees Collected: {sum(tx.get_fee(blockchain.utxo_set) for tx in block2.transactions[1:]) if len(block2.transactions) > 1 else 0} coins")

        print(f"\nUpdated Balances:")
        print(f"  Wallet 1: {blockchain.get_balance(wallet1.get_address())} coins")
        print(f"  Wallet 2: {blockchain.get_balance(wallet2.get_address())} coins")
        print(f"  Wallet 3: {blockchain.get_balance(wallet3.get_address())} coins")

    print_separator()
    print("MORE TRANSACTIONS")
    print_separator()

    print("\nTransaction 3: Wallet 2 → Wallet 3 (10 coins, 0.3 fee)")
    tx3 = wallet2.create_transaction(wallet3.get_address(), 10, 0.3, blockchain)
    if tx3:
        blockchain.add_transaction(tx3)
        print(f"  Transaction ID: {tx3.tx_id}")

    print("\nTransaction 4: Wallet 3 → Wallet 1 (5 coins, 0.2 fee)")
    tx4 = wallet3.create_transaction(wallet1.get_address(), 5, 0.2, blockchain)
    if tx4:
        blockchain.add_transaction(tx4)
        print(f"  Transaction ID: {tx4.tx_id}")

    print_separator()
    print("MINING BLOCK 3")
    print_separator()

    block3 = blockchain.mine_block(wallet3.get_address())
    if block3:
        database.save_block(block3)
        print(f"\nBlock 3 Details:")
        print(f"  Hash: {block3.hash}")
        print(f"  Merkle Root: {block3.merkle_root}")
        print(f"  Transactions: {len(block3.transactions)}")

        print(f"\nFinal Balances:")
        print(f"  Wallet 1: {blockchain.get_balance(wallet1.get_address())} coins")
        print(f"  Wallet 2: {blockchain.get_balance(wallet2.get_address())} coins")
        print(f"  Wallet 3: {blockchain.get_balance(wallet3.get_address())} coins")

    print_separator()
    print("BLOCKCHAIN STATISTICS")
    print_separator()

    info = blockchain.get_chain_info()
    print(f"Total Blocks: {info['length']}")
    print(f"Current Difficulty: {info['difficulty']}")
    print(f"Block Reward: {info['block_reward']} coins")
    print(f"Mempool Size: {info['mempool_size']} transactions")
    print(f"Total UTXOs: {info['utxo_count']}")
    print(f"Chain Valid: {info['is_valid']}")

    mining_stats = blockchain.get_mining_stats()
    print(f"\nMining Statistics:")
    print(f"  Average Block Time: {mining_stats['average_block_time']:.2f} seconds")
    print(f"  Total Blocks: {mining_stats['total_blocks']}")

    total_supply = sum(utxo.amount for utxo in blockchain.utxo_set.values())
    print(f"\nEconomic Statistics:")
    print(f"  Total Supply: {total_supply} coins")
    print(f"  Unique Addresses: {len(set(utxo.address for utxo in blockchain.utxo_set.values()))}")

    print_separator()
    print("UTXO DETAILS FOR EACH WALLET")
    print_separator()

    for i, wallet in enumerate([wallet1, wallet2, wallet3], 1):
        address = wallet.get_address()
        utxos = blockchain.get_utxos_for_address(address)
        print(f"\nWallet {i} ({address[:16]}...):")
        print(f"  Total Balance: {blockchain.get_balance(address)} coins")
        print(f"  Number of UTXOs: {len(utxos)}")
        for tx_id, output_idx, amount in utxos:
            print(f"    - UTXO: {tx_id[:16]}...:{output_idx} = {amount} coins")

    print_separator()
    print("BLOCKCHAIN DETAILS")
    print_separator()

    for block in blockchain.chain:
        print(f"\nBlock {block.index}:")
        print(f"  Hash: {block.hash}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Merkle Root: {block.merkle_root}")
        print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}")
        print(f"  Nonce: {block.nonce}")
        print(f"  Transactions: {len(block.transactions)}")
        for j, tx in enumerate(block.transactions):
            print(f"    TX {j}: {tx.tx_id[:32]}...")
            print(f"      Inputs: {len(tx.inputs)}, Outputs: {len(tx.outputs)}")

    print_separator()
    print("WALLET EXPORT DEMO")
    print_separator()

    print("Exporting Wallet 1 to file...")
    wallet1.export_to_file("wallet1_backup.json")
    print("Wallet exported successfully!")

    print("\nImporting wallet from file...")
    imported_wallet = AdvancedWallet.import_from_file("wallet1_backup.json")
    print(f"Imported wallet address: {imported_wallet.get_address()}")
    print(f"Address matches: {imported_wallet.get_address() == wallet1.get_address()}")

    print_separator()
    print("DEMONSTRATION COMPLETE!")
    print_separator()

    print("\nKey Features Demonstrated:")
    print("  ✓ ECDSA Digital Signatures")
    print("  ✓ UTXO Transaction Model")
    print("  ✓ Transaction Mempool")
    print("  ✓ Merkle Tree Block Verification")
    print("  ✓ Proof-of-Work Mining")
    print("  ✓ Transaction Fees")
    print("  ✓ SQLite Persistence")
    print("  ✓ Wallet Import/Export")
    print("  ✓ Balance Tracking")
    print("  ✓ Chain Validation")

    print("\nDatabase saved to: demo_blockchain.db")
    print("To start the REST API server, run: python api.py")

    database.close()


if __name__ == "__main__":
    main()
