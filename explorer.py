#!/usr/bin/env python3

import sqlite3
import sys

def show_blockchain_explorer(db_file='live_blockchain.db'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("🔍 CRYPTOCURRENCY BLOCKCHAIN EXPLORER")
    print("="*80)

    # Get blockchain stats
    cursor.execute('SELECT COUNT(*) FROM blocks')
    total_blocks = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM transactions')
    total_txs = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(amount) FROM utxos')
    total_supply = cursor.fetchone()[0] or 0

    cursor.execute('SELECT COUNT(DISTINCT address) FROM utxos')
    unique_addresses = cursor.fetchone()[0]

    print(f"\n📊 BLOCKCHAIN STATISTICS")
    print(f"   Total Blocks: {total_blocks}")
    print(f"   Total Transactions: {total_txs}")
    print(f"   Total Supply: {total_supply} coins")
    print(f"   Unique Addresses: {unique_addresses}")

    # Show all blocks
    print(f"\n⛓️  ALL BLOCKS")
    cursor.execute('''
        SELECT block_index, block_hash, timestamp, nonce,
               (SELECT COUNT(*) FROM transactions WHERE block_index = blocks.block_index)
        FROM blocks
        ORDER BY block_index
    ''')

    for idx, hash, ts, nonce, tx_count in cursor.fetchall():
        from datetime import datetime
        dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n   Block #{idx}")
        print(f"      Hash: {hash[:60]}...")
        print(f"      Time: {dt}")
        print(f"      Nonce: {nonce}")
        print(f"      Transactions: {tx_count}")

    # Show all addresses with balances
    print(f"\n💰 ALL COIN HOLDERS")
    cursor.execute('''
        SELECT address, SUM(amount) as balance, COUNT(*) as utxo_count
        FROM utxos
        GROUP BY address
        ORDER BY balance DESC
    ''')

    for i, (addr, balance, utxo_count) in enumerate(cursor.fetchall(), 1):
        print(f"\n   Address #{i}")
        print(f"      {addr}")
        print(f"      Balance: {balance} coins ({utxo_count} UTXOs)")

    # Show recent transactions
    print(f"\n📝 RECENT TRANSACTIONS")
    cursor.execute('''
        SELECT tx_id, timestamp, block_index
        FROM transactions
        ORDER BY timestamp DESC
        LIMIT 10
    ''')

    for tx_id, ts, block_idx in cursor.fetchall():
        from datetime import datetime
        dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n   TX: {tx_id[:50]}...")
        print(f"      Block: {block_idx} | Time: {dt}")

    print("\n" + "="*80)
    conn.close()

if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else 'live_blockchain.db'
    try:
        show_blockchain_explorer(db_file)
    except Exception as e:
        print(f"Error: {e}")
        print(f"Usage: python3 explorer.py [database_file]")
