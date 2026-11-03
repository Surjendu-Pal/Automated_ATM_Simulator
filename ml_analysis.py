"""Optional educational anomaly analysis; never treats a prediction as proven fraud."""
import csv
from pathlib import Path


def analyze(history, csv_path=None):
    try:
        import pandas as pd
        from sklearn.ensemble import IsolationForest
    except ImportError as exc:
        raise RuntimeError('Install optional ML packages: pip install -r requirements.txt') from exc
    records = [{'reference': item['reference'], 'kind': item['kind'],
                'amount_rupees': item['amount_paise'] / 100,
                'date_time': item['created_at']} for item in reversed(history)]
    if not records:
        return [], 'No transactions yet. Complete some demo operations first.'
    df = pd.DataFrame(records)
    if len(df) < 8:
        df['status'] = 'Insufficient data'
        msg = 'At least 8 transactions are needed before fitting the demo model.'
    else:
        model = IsolationForest(n_estimators=100, contamination=0.15, random_state=42)
        df['status'] = ['Review' if x == -1 else 'Typical'
                        for x in model.fit_predict(df[['amount_rupees']])]
        msg = 'Review means statistically unusual in this small sample, not fraudulent.'
    if csv_path:
        df.to_csv(csv_path, index=False)
    return df.to_dict(orient='records'), msg


if __name__ == '__main__':
    from database import initialize
    from atm_operations import ATMService
    initialize()
    rows, note = analyze(ATMService().history('1001'), 'transaction_analysis.csv')
    print(note)
    for row in rows:
        print(row)
