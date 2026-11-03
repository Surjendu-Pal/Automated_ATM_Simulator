# Automated ATM Transaction Simulator

Professional **educational simulator** for a group of four, built with Python Tkinter, SQLite and optional scikit-learn. **No real financial accounts, ATM hardware or payments are connected.**

## Getting started (Windows / VS Code)

1. Install Python 3.10+ from python.org, enabling **Add Python to PATH**.
2. Unzip the folder; open `Automated_ATM_Simulator` in VS Code.
3. Open Terminal and run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

On macOS/Linux, activate with `source .venv/bin/activate` and run `python3 main.py`.

Tkinter and sqlite3 normally ship with desktop Python. On Ubuntu, install `python3-tk` if Tkinter is missing. Running the app creates `atm_database.db` automatically.

## Demo account details (fictional only)

| Account | PIN | Starting balance |
| --- | --- | --- |
| 1001 | 1234 | INR 10,000.00 |
| 1002 | 5678 | INR 5,000.00 |

These credentials are **only for this classroom demonstration**. PINs are stored as salted PBKDF2 hashes, not plaintext. Three incorrect attempts lock the account; delete `atm_database.db` while the app is closed to reset the *demo* database. **Doing so erases all demo transactions and changed PINs.**

## Features

PIN login, balance check, deposits, withdrawals, atomic transfers, 5-item mini statement, full history, PIN change, receipt text-file export, logout, optional Isolation Forest anomaly review and CSV export. SQLite uses integer paise for exact money calculations. Transfer debits and credits share a single database transaction; errors roll back both.

## Machine learning

Go to **ML Risk Analysis** after making 8 or more demo transactions. This feature fits an Isolation Forest to transaction **amounts only**, shows *Typical* or *Review*, and saves `transaction_analysis.csv`. With fewer than 8 records it reports *Insufficient data*. The sample is small, and anomalies **are not proof of fraud**. For the viva, describe unsupervised anomaly detection and its limitations.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Main files

- `main.py` — desktop GUI
- `database.py` — database schema, demo accounts, PIN hashing
- `atm_operations.py` — validation, atomic financial operations, history
- `ml_analysis.py` — Isolation Forest and CSV output
- `tests/test_atm.py` — automated unit tests
- `documentation/Project_Report.pdf` — submission report with group placeholders
- `screenshots/SCREENSHOT_CHECKLIST.md` — screenshots to capture on your computer

## Responsibilities (4 students)

1. Group member 1: UI and Tkinter workflow.
2. Group member 2: SQLite and transaction validation.
3. Group member 3: ML analysis and evaluation/limitations.
4. Group member 4: testing, diagrams, report and demonstration.

Replace placeholders in the report with your actual names and institutional details. Each student should understand the complete project for the viva.

## Submission

Run the tests, perform the demo steps in the screenshot checklist, capture actual screenshots, fill the group details in the editable report information file, then submit the project ZIP to the teacher's instructed Google Drive folder. Never include real PINs, banking data or passwords. The supplied database is generated locally and not bundled.

## Production limitations

Not a real bank, no hardware dispensing, online banking, audit-grade security, server-side access control or real fraud classification. This software is strictly for coursework.
