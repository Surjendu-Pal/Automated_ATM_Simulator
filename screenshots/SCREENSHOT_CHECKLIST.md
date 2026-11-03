# Screenshot Checklist (capture from the actual running desktop app)

Save screenshots as PNGs inside this folder. Use Windows `Win + Shift + S` or Snipping Tool. Do **not** submit reference/mock screenshots as actual outputs.

- [ ] `01_login.png`: application login screen, demo account information visible.
- [ ] `02_dashboard.png`: successful login and balance displayed.
- [ ] `03_deposit.png`: completed deposit confirmation (e.g. INR 1,500).
- [ ] `04_withdrawal.png`: completed withdrawal confirmation (e.g. INR 500).
- [ ] `05_transfer.png`: transfer confirmation to demo account 1002.
- [ ] `06_mini_statement.png`: five most recent transactions.
- [ ] `07_history.png`: full transaction history window.
- [ ] `08_pin_change.png`: success confirmation; never expose the PIN itself.
- [ ] `09_ml_analysis.png`: ML analysis table after at least 8 transactions.
- [ ] `10_csv.png`: generated CSV open in VS Code / spreadsheet.
- [ ] `11_tests.png`: successful unit test output in VS Code terminal.
- [ ] `12_receipt.png`: saved demo receipt open as text (no real account data).

## Suggested demo sequence

Login 1001/1234; deposit 1500, withdraw 500, transfer 250 to 1002; run a few small deposits/withdrawals until transaction count is 8; check history and ML; optionally change PIN at end. For an unusual-amount example, you may use a *demo* deposit of 40,000, but prediction is data-dependent and is not guaranteed to be `Review`. Use the actual app results in the report.
