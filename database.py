"""SQLite data layer for a fictional-money, educational ATM."""
import sqlite3
import hashlib
import hmac
import os
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / 'atm_database.db'


def pin_hash(pin, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', pin.encode('utf-8'), salt, 210_000)
    return salt.hex() + ':' + digest.hex()


def verify_pin(pin, stored):
    try:
        salt_hex, expected = stored.split(':', 1)
        actual = pin_hash(pin, bytes.fromhex(salt_hex)).split(':', 1)[1]
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def connect(path=None):
    conn = sqlite3.connect(str(path or DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def initialize(path=None):
    with connect(path) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS accounts (
          account_no TEXT PRIMARY KEY, name TEXT NOT NULL,
          pin_hash TEXT NOT NULL, balance_paise INTEGER NOT NULL CHECK(balance_paise >= 0),
          failed_attempts INTEGER NOT NULL DEFAULT 0,
          locked INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS transactions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          account_no TEXT NOT NULL REFERENCES accounts(account_no),
          kind TEXT NOT NULL, amount_paise INTEGER NOT NULL CHECK(amount_paise > 0),
          note TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL,
          reference TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tx_account_id ON transactions(account_no, id DESC);
        ''')
        for number, name, pin, amount in [
            ('1001', 'Demo User', '1234', 1000000),
            ('1002', 'Sample Recipient', '5678', 500000),
        ]:
            conn.execute('''INSERT OR IGNORE INTO accounts
              (account_no,name,pin_hash,balance_paise) VALUES(?,?,?,?)''',
              (number, name, pin_hash(pin), amount))


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')
