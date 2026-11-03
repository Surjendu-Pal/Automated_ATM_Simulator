import tempfile
import unittest
from pathlib import Path
from database import initialize
from atm_operations import ATMService, ATMError, amount_to_paise

class ATMTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.sqlite3'
        initialize(self.path)
        self.svc = ATMService(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_login(self):
        self.assertEqual(self.svc.authenticate('1001', '1234')['name'], 'Demo User')
        with self.assertRaises(ATMError):
            self.svc.authenticate('1001', '9999')

    def test_deposit_withdraw(self):
        self.svc.transact('1001', 'DEPOSIT', '20.25')
        self.svc.transact('1001', 'WITHDRAW', '5.50')
        self.assertEqual(self.svc.balance('1001'), 1001475)

    def test_transfer_atomic(self):
        self.svc.transact('1001', 'TRANSFER', '100', '1002')
        self.assertEqual(self.svc.balance('1001'), 990000)
        self.assertEqual(self.svc.balance('1002'), 510000)
        self.assertEqual(len(self.svc.history('1002')), 1)

    def test_rejected_operations(self):
        for amount in ['-1', '0', 'nan', '1.999', 'hello']:
            with self.assertRaises(ATMError):
                amount_to_paise(amount)
        with self.assertRaises(ATMError):
            self.svc.transact('1001', 'WITHDRAW', '20000')
        with self.assertRaises(ATMError):
            self.svc.transact('1001', 'TRANSFER', '10', '9999')
        self.assertEqual(self.svc.balance('1001'), 1000000)

    def test_change_pin_and_lock(self):
        self.svc.change_pin('1001', '1234', '4321')
        self.assertEqual(self.svc.authenticate('1001', '4321')['account_no'], '1001')
        for _ in range(3):
            with self.assertRaises(ATMError):
                self.svc.authenticate('1002', '0000')
        with self.assertRaises(ATMError):
            self.svc.authenticate('1002', '5678')

if __name__ == '__main__':
    unittest.main()
