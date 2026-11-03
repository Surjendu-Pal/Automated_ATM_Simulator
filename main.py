"""Professional classroom ATM simulation: Tkinter, SQLite and optional ML."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path
from datetime import datetime
from atm_operations import ATMService, ATMError, money
from database import initialize
from ml_analysis import analyze

ROOT = Path(__file__).resolve().parent
NAVY = '#10233f'
BLUE = '#2364d2'
BG = '#f3f6fc'

class ATMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ATM Pro | Educational Transaction Simulator')
        self.geometry('1040x700')
        self.minsize(850, 580)
        self.configure(bg=BG)
        self.service = ATMService()
        self.account = None
        self.name = None
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('Treeview', rowheight=31, font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def title_label(self, parent, text, size=24):
        return tk.Label(parent, text=text, fg=NAVY, bg=BG, font=('Segoe UI', size, 'bold'))

    def btn(self, parent, text, command, bg=BLUE, width=19):
        return tk.Button(parent, text=text, command=command, bg=bg, fg='white',
                         activebackground=NAVY, activeforeground='white',
                         bd=0, font=('Segoe UI', 11, 'bold'), pady=12,
                         width=width, cursor='hand2')

    def show_login(self):
        self.account = None
        self.name = None
        self.clear()
        outer = tk.Frame(self, bg=BG)
        outer.place(relx=.5, rely=.47, anchor='center')
        tk.Label(outer, text='ATM PRO', font=('Segoe UI', 35, 'bold'), bg=BG, fg=NAVY).pack(pady=(0, 5))
        tk.Label(outer, text='SECURE DEMO BANKING • NO REAL MONEY', font=('Segoe UI', 10),
                 bg=BG, fg='#65748a').pack(pady=(0, 32))
        tk.Label(outer, text='Account number', bg=BG, fg=NAVY).pack(anchor='w')
        account_entry = ttk.Entry(outer, width=37, font=('Segoe UI', 13))
        account_entry.pack(pady=(5, 16), ipady=6)
        tk.Label(outer, text='4-digit PIN', bg=BG, fg=NAVY).pack(anchor='w')
        pin_entry = ttk.Entry(outer, width=37, font=('Segoe UI', 13), show='●')
        pin_entry.pack(pady=(5, 20), ipady=6)
        def login(event=None):
            try:
                user = self.service.authenticate(account_entry.get().strip(), pin_entry.get())
                self.account, self.name = user['account_no'], user['name']
                self.show_dashboard()
            except ATMError as exc:
                messagebox.showerror('Login failed', str(exc))
                pin_entry.delete(0, tk.END)
        self.btn(outer, 'LOGIN', login, width=30).pack()
        pin_entry.bind('<Return>', login)
        tk.Label(outer, text='Demo accounts: 1001 / 1234  |  1002 / 5678',
                 bg=BG, fg='#65748a', font=('Segoe UI', 10)).pack(pady=22)
        account_entry.focus_set()

    def show_dashboard(self):
        self.clear()
        header = tk.Frame(self, bg=NAVY, height=96)
        header.pack(fill='x')
        tk.Label(header, text='ATM PRO  /  TRANSACTION SIMULATOR', font=('Segoe UI', 18, 'bold'),
                 bg=NAVY, fg='white').pack(side='left', padx=35, pady=27)
        self.btn(header, 'LOG OUT', self.show_login, '#b34055', width=11).pack(side='right', padx=30)
        body = tk.Frame(self, bg=BG)
        body.pack(fill='both', expand=True, padx=38, pady=30)
        self.title_label(body, f'Welcome, {self.name}').pack(anchor='w')
        tk.Label(body, text=f'Demo account  •  {self.account}', bg=BG, fg='#697b91',
                 font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 24))
        self.balance_label = tk.Label(body, bg=BG, fg=NAVY, font=('Segoe UI', 29, 'bold'))
        self.balance_label.pack(anchor='w', pady=(0, 26))
        self.refresh_balance()
        tiles = tk.Frame(body, bg=BG)
        tiles.pack(anchor='w', fill='x')
        operations = [
            ('Check Balance', lambda: self.refresh_balance(True)),
            ('Withdraw', lambda: self.amount_action('WITHDRAW')),
            ('Deposit', lambda: self.amount_action('DEPOSIT')),
            ('Transfer', lambda: self.amount_action('TRANSFER')),
            ('Mini Statement', lambda: self.show_history(5)),
            ('All Transactions', lambda: self.show_history(200)),
            ('Change PIN', self.pin_change),
            ('ML Risk Analysis', self.ml_window),
        ]
        for i, (caption, action) in enumerate(operations):
            self.btn(tiles, caption, action, width=19).grid(row=i // 4, column=i % 4,
                         padx=8, pady=10, sticky='nsew')
            tiles.columnconfigure(i % 4, weight=1)
        tk.Label(body, text='Educational simulator only. Transactions update a local SQLite demo database.',
                 fg='#68788f', bg=BG, font=('Segoe UI', 10)).pack(anchor='w', pady=33)

    def refresh_balance(self, notify=False):
        balance = money(self.service.balance(self.account))
        self.balance_label.configure(text=f'Available Balance   {balance}')
        if notify:
            messagebox.showinfo('Balance', f'Your demo balance is {balance}')

    def amount_action(self, kind):
        amount = simpledialog.askstring(kind.title(), 'Enter amount in rupees (e.g., 1250.50):', parent=self)
        if amount is None:
            return
        recipient = None
        if kind == 'TRANSFER':
            recipient = simpledialog.askstring('Recipient', 'Enter recipient account number:', parent=self)
            if recipient is None:
                return
            recipient = recipient.strip()
        try:
            result = self.service.transact(self.account, kind, amount, recipient)
            self.refresh_balance()
            messagebox.showinfo('Transaction successful',
                f"{kind.title()} {money(result['amount_paise'])}\n"
                f"New balance: {money(result['balance_paise'])}\n"
                f"Reference: {result['reference']}")
            if messagebox.askyesno('Receipt', 'Save this transaction receipt as a text file?'):
                self.save_receipt(result)
        except ATMError as exc:
            messagebox.showerror('Transaction rejected', str(exc))

    def save_receipt(self, result):
        out = filedialog.asksaveasfilename(parent=self, title='Save demo receipt',
              initialdir=str(ROOT / 'receipts'),
              initialfile=f"receipt_{result['reference']}.txt", defaultextension='.txt',
              filetypes=[('Text files', '*.txt')])
        if out:
            content = ('ATM PRO - DEMO RECEIPT (NOT REAL BANKING)\n'
                       f"Reference: {result['reference']}\nDate: {result['date_time']}\n"
                       f"Account: {result['account_no']}\nType: {result['kind']}\n"
                       f"Amount: {money(result['amount_paise'])}\n"
                       f"Recipient: {result['recipient'] or 'N/A'}\n"
                       f"Remaining balance: {money(result['balance_paise'])}\n")
            Path(out).write_text(content, encoding='utf-8')
            messagebox.showinfo('Receipt', 'Demo receipt saved successfully.')

    def pin_change(self):
        old = simpledialog.askstring('Change PIN', 'Enter current PIN:', show='*', parent=self)
        if old is None:
            return
        new = simpledialog.askstring('Change PIN', 'Enter new 4-digit PIN:', show='*', parent=self)
        if new is None:
            return
        confirm = simpledialog.askstring('Change PIN', 'Confirm new PIN:', show='*', parent=self)
        if confirm is None:
            return
        if new != confirm:
            messagebox.showerror('Change PIN', 'New PINs do not match.')
            return
        try:
            self.service.change_pin(self.account, old, new)
            messagebox.showinfo('Change PIN', 'PIN changed. Use your new PIN next time you log in.')
        except ATMError as exc:
            messagebox.showerror('Change PIN', str(exc))

    def table_window(self, heading, columns, rows):
        window = tk.Toplevel(self)
        window.title(heading)
        window.geometry('990x510')
        window.configure(bg=BG)
        self.title_label(window, heading, 20).pack(anchor='w', padx=20, pady=20)
        frame = tk.Frame(window, bg=BG)
        frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        table = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=145, anchor='w')
        ybar = ttk.Scrollbar(frame, orient='vertical', command=table.yview)
        table.configure(yscrollcommand=ybar.set)
        ybar.pack(side='right', fill='y')
        table.pack(fill='both', expand=True)
        for row in rows:
            table.insert('', 'end', values=row)
        return window

    def show_history(self, limit):
        history = self.service.history(self.account, limit)
        columns = ('Date (UTC)', 'Type', 'Amount', 'Details', 'Reference')
        rows = [(t['created_at'][:19].replace('T', ' '), t['kind'],
                 money(t['amount_paise']), t['note'], t['reference']) for t in history]
        self.table_window('Mini Statement' if limit == 5 else 'Transaction History', columns, rows)

    def ml_window(self):
        try:
            path = ROOT / 'transaction_analysis.csv'
            rows, note = analyze(self.service.history(self.account, 200), path)
        except (RuntimeError, ValueError) as exc:
            messagebox.showerror('ML Analysis', str(exc))
            return
        columns = ('Date (UTC)', 'Type', 'Amount (INR)', 'Anomaly Status', 'Reference')
        view = [(r['date_time'][:19].replace('T', ' '), r['kind'],
                 f"{r['amount_rupees']:,.2f}", r['status'], r['reference']) for r in rows]
        self.table_window('ML: Transaction Anomaly Review', columns, view)
        messagebox.showinfo('ML Analysis', note + '\nCSV saved to transaction_analysis.csv')

if __name__ == '__main__':
    initialize()
    ATMApp().mainloop()
