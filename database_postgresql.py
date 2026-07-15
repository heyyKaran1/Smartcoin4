import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class PostgreSQLDatabase:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            if 'postgresql://' in self.database_url:
                self.conn = psycopg2.connect(self.database_url)
            else:
                # Fallback to SQLite for development
                from database import Database
                self.conn = Database(self.database_url)
                self.is_postgres = False
                return

            self.is_postgres = True
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"⚠️  PostgreSQL connection failed: {e}")
            print("Falling back to SQLite...")
            from database import Database
            self.conn = Database("blockchain.db")
            self.is_postgres = False

    def create_tables(self):
        """Create database schema"""
        if not self.is_postgres:
            return

        cursor = self.conn.cursor()

        # Blocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id SERIAL PRIMARY KEY,
                block_index INTEGER UNIQUE NOT NULL,
                hash VARCHAR(64) NOT NULL,
                previous_hash VARCHAR(64) NOT NULL,
                merkle_root VARCHAR(64) NOT NULL,
                timestamp DOUBLE PRECISION NOT NULL,
                nonce INTEGER NOT NULL,
                difficulty INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                tx_id VARCHAR(64) UNIQUE NOT NULL,
                block_index INTEGER,
                timestamp DOUBLE PRECISION NOT NULL,
                inputs JSONB,
                outputs JSONB,
                merchant_details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (block_index) REFERENCES blocks(block_index)
            )
        ''')

        # UTXOs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utxos (
                id SERIAL PRIMARY KEY,
                utxo_key VARCHAR(128) UNIQUE NOT NULL,
                address VARCHAR(64) NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                tx_id VARCHAR(64) NOT NULL,
                output_index INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Users table (for authentication)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Wallets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id SERIAL PRIMARY KEY,
                address VARCHAR(64) UNIQUE NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Token balances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_balances (
                id SERIAL PRIMARY KEY,
                address VARCHAR(64) NOT NULL,
                token_symbol VARCHAR(10) NOT NULL,
                balance DOUBLE PRECISION DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(address, token_symbol)
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_tx_id ON transactions(tx_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_utxos_address ON utxos(address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_balances_address ON token_balances(address)')

        self.conn.commit()
        cursor.close()
        print("✅ PostgreSQL schema created")

    def save_block(self, block):
        """Save block to database"""
        if not self.is_postgres:
            return self.conn.save_block(block)

        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO blocks (block_index, hash, previous_hash, merkle_root,
                                   timestamp, nonce, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (block_index) DO NOTHING
            ''', (block.index, block.hash, block.previous_hash, block.merkle_root,
                  block.timestamp, block.nonce, 2))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving block: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def save_utxo(self, utxo_key, address, amount, tx_id, output_index):
        """Save UTXO to database"""
        if not self.is_postgres:
            return self.conn.save_utxo(utxo_key, address, amount, tx_id, output_index)

        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO utxos (utxo_key, address, amount, tx_id, output_index)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (utxo_key) DO NOTHING
            ''', (utxo_key, address, amount, tx_id, output_index))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving UTXO: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def delete_utxo(self, utxo_key):
        """Delete UTXO from database"""
        if not self.is_postgres:
            return self.conn.delete_utxo(utxo_key)

        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM utxos WHERE utxo_key = %s', (utxo_key,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting UTXO: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def get_all_utxos(self):
        """Get all UTXOs"""
        if not self.is_postgres:
            return self.conn.get_all_utxos()

        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM utxos')
        utxos = cursor.fetchall()
        cursor.close()
        return utxos

    def close(self):
        """Close database connection"""
        if self.is_postgres and self.conn:
            self.conn.close()
