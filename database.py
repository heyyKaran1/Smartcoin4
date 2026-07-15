import sqlite3
import json
from typing import Optional, List
from block import Block
from transaction import Transaction


class Database:
    def __init__(self, db_file: str = "blockchain.db"):
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_index INTEGER PRIMARY KEY,
                block_hash TEXT UNIQUE NOT NULL,
                previous_hash TEXT NOT NULL,
                timestamp REAL NOT NULL,
                nonce INTEGER NOT NULL,
                merkle_root TEXT NOT NULL,
                block_data TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                block_index INTEGER,
                timestamp REAL NOT NULL,
                tx_data TEXT NOT NULL,
                FOREIGN KEY (block_index) REFERENCES blocks (block_index)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utxos (
                utxo_key TEXT PRIMARY KEY,
                address TEXT NOT NULL,
                amount REAL NOT NULL,
                tx_id TEXT NOT NULL,
                output_index INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(block_hash)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_block ON transactions(block_index)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_utxos_address ON utxos(address)
        ''')

        self.connection.commit()

    def save_block(self, block: Block):
        cursor = self.connection.cursor()

        block_data = json.dumps(block.to_dict())

        cursor.execute('''
            INSERT OR REPLACE INTO blocks
            (block_index, block_hash, previous_hash, timestamp, nonce, merkle_root, block_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (block.index, block.hash, block.previous_hash, block.timestamp,
              block.nonce, block.merkle_root, block_data))

        for tx in block.transactions:
            tx_data = json.dumps(tx.to_dict())
            cursor.execute('''
                INSERT OR REPLACE INTO transactions
                (tx_id, block_index, timestamp, tx_data)
                VALUES (?, ?, ?, ?)
            ''', (tx.tx_id, block.index, tx.timestamp, tx_data))

        self.connection.commit()

    def get_block_by_index(self, index: int) -> Optional[Block]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT block_data FROM blocks WHERE block_index = ?', (index,))
        row = cursor.fetchone()

        if row:
            block_dict = json.loads(row[0])
            return Block.from_dict(block_dict)
        return None

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT block_data FROM blocks WHERE block_hash = ?', (block_hash,))
        row = cursor.fetchone()

        if row:
            block_dict = json.loads(row[0])
            return Block.from_dict(block_dict)
        return None

    def get_all_blocks(self) -> List[Block]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT block_data FROM blocks ORDER BY block_index')
        rows = cursor.fetchall()

        blocks = []
        for row in rows:
            block_dict = json.loads(row[0])
            blocks.append(Block.from_dict(block_dict))
        return blocks

    def get_transaction_by_id(self, tx_id: str) -> Optional[Transaction]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT tx_data FROM transactions WHERE tx_id = ?', (tx_id,))
        row = cursor.fetchone()

        if row:
            tx_dict = json.loads(row[0])
            return Transaction.from_dict(tx_dict)
        return None

    def save_utxo(self, utxo_key: str, address: str, amount: float, tx_id: str, output_index: int):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO utxos
            (utxo_key, address, amount, tx_id, output_index)
            VALUES (?, ?, ?, ?, ?)
        ''', (utxo_key, address, amount, tx_id, output_index))
        self.connection.commit()

    def delete_utxo(self, utxo_key: str):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM utxos WHERE utxo_key = ?', (utxo_key,))
        self.connection.commit()

    def get_utxos_by_address(self, address: str) -> List[tuple]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT tx_id, output_index, amount
            FROM utxos
            WHERE address = ?
        ''', (address,))
        return cursor.fetchall()

    def get_all_utxos(self) -> dict:
        cursor = self.connection.cursor()
        cursor.execute('SELECT utxo_key, address, amount FROM utxos')
        rows = cursor.fetchall()

        utxos = {}
        for row in rows:
            from transaction import TransactionOutput
            utxos[row[0]] = TransactionOutput(row[1], row[2])
        return utxos

    def get_block_count(self) -> int:
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM blocks')
        return cursor.fetchone()[0]

    def close(self):
        self.connection.close()
