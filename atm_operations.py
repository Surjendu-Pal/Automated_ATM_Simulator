"""Banking rules. Balances in integer paise: never use binary floats for money."""
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from database import connect, verify_pin, pin_hash, timestamp

class ATMError(Exception):
    pass


def amount_to_paise(raw):
    try:
        value = Decimal(str(raw))
        if not value.is_finite() or value <= 0 or value.as_tuple().exponent < -2:
            raise ATMError('Enter a positive amount with at most two decimal places.')
        paise = int(value * 100)
        if paise > 10_000_000_00:
            raise ATMError('Amount exceeds the demo transaction limit.')
        return paise
    except (InvalidOperation, ValueError, TypeError):
        raise ATMError('Enter a valid amount.') from None


def money(paise):
    return f'₹{paise / 100:,.2f}'


class ATMService:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def authenticate(self, account_no, pin):
        with connect(self.db_path) as db:
            row = db.execute('SELECT * FROM accounts WHERE account_no=?', (account_no,)).fetchone()
            if not row:
                raise ATMError('Invalid account number or PIN.')
            if row['locked']:
                raise ATMError('Demo account locked after 3 failures. Reset the demo database to unlock.')
            if not verify_pin(pin, row['pin_hash']):
                failures = row['failed_attempts'] + 1
                db.execute('UPDATE accounts SET failed_attempts=?,locked=? WHERE account_no=?',
                           (failures, int(failures >= 3), account_no))
                db.commit()
                raise ATMError('Invalid account number or PIN.')
            db.execute('UPDATE accounts SET failed_attempts=0 WHERE account_no=?', (account_no,))
            return {'account_no': row['account_no'], 'name': row['name']}

    def balance(self, account_no):
        with connect(self.db_path) as db:
            row = db.execute('SELECT balance_paise FROM accounts WHERE account_no=?', (account_no,)).fetchone()
            if row is None:
                raise ATMError('Account not found.')
            return row['balance_paise']

    def _record(self, db, account, kind, amount, note, reference):
        db.execute('''INSERT INTO transactions
          (account_no,kind,amount_paise,note,created_at,reference) VALUES(?,?,?,?,?,?)''',
          (account, kind, amount, note, timestamp(), reference))

    def transact(self, account, kind, amount_raw, recipient=None):
        if kind not in ('DEPOSIT', 'WITHDRAW', 'TRANSFER'):
            raise ATMError('Unknown transaction type.')
        amount = amount_to_paise(amount_raw)
        if kind == 'TRANSFER' and (not recipient or recipient == account):
            raise ATMError('Enter a different recipient account.')
        reference = uuid4().hex[:12].upper()
        with connect(self.db_path) as db:
            db.execute('BEGIN IMMEDIATE')
            sender = db.execute('SELECT balance_paise FROM accounts WHERE account_no=?', (account,)).fetchone()
            if sender is None:
                raise ATMError('Account not found.')
            if kind == 'TRANSFER' and not db.execute('SELECT 1 FROM accounts WHERE account_no=?', (recipient,)).fetchone():
                raise ATMError('Recipient account not found.')
            if kind != 'DEPOSIT' and sender['balance_paise'] < amount:
                raise ATMError('Insufficient balance.')
            delta = amount if kind == 'DEPOSIT' else -amount
            db.execute('UPDATE accounts SET balance_paise=balance_paise+? WHERE account_no=?', (delta, account))
            note = f'To account {recipient}' if kind == 'TRANSFER' else 'Demo ATM operation'
            self._record(db, account, kind, amount, note, reference)
            if kind == 'TRANSFER':
                db.execute('UPDATE accounts SET balance_paise=balance_paise+? WHERE account_no=?', (amount, recipient))
                self._record(db, recipient, 'TRANSFER_IN', amount, f'From account {account}', reference)
            updated = db.execute('SELECT balance_paise FROM accounts WHERE account_no=?', (account,)).fetchone()[0]
        return {'reference': reference, 'kind': kind, 'amount_paise': amount,
                'balance_paise': updated, 'account_no': account, 'recipient': recipient,
                'date_time': timestamp()}

    def history(self, account, limit=100):
        with connect(self.db_path) as db:
            rows = db.execute('''SELECT * FROM transactions WHERE account_no=? ORDER BY id DESC LIMIT ?''',
                              (account, limit)).fetchall()
            return [dict(row) for row in rows]

    def change_pin(self, account, old_pin, new_pin):
        if not (new_pin.isdigit() and len(new_pin) == 4):
            raise ATMError('New PIN must have exactly 4 digits.')
        with connect(self.db_path) as db:
            row = db.execute('SELECT pin_hash FROM accounts WHERE account_no=?', (account,)).fetchone()
            if row is None or not verify_pin(old_pin, row[0]):
                raise ATMError('Current PIN is incorrect.')
            if old_pin == new_pin:
                raise ATMError('New PIN must differ from the current PIN.')
            db.execute('UPDATE accounts SET pin_hash=? WHERE account_no=?', (pin_hash(new_pin), account))
