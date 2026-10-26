"""Download only Elexon WINDFOR and WIND FUELHH. Atomic, reproducible snapshot."""
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
BASE = 'https://data.elexon.co.uk/bmrs/api/v1/datasets/'

def fetch(dataset, params):
    url = BASE + dataset + '/stream?' + urlencode(params)
    for attempt in range(4):
        try:
            with urlopen(url, timeout=90) as response:
                rows = json.load(response)
            if not isinstance(rows, list) or not rows:
                raise ValueError(f'Unexpected empty response: {url}')
            return rows, url
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def main():
    DATA.mkdir(exist_ok=True)
    forecasts, actuals, sources = [], [], []
    # Include one preceding publication day for fallback forecasts at early cutoffs.
    for day in range(32):
        start = datetime(2025, 12, 31) + timedelta(days=day)
        end = start + timedelta(days=1)
        rows, url = fetch('WINDFOR', {'publishDateTimeFrom': start.isoformat()+'Z', 'publishDateTimeTo': end.isoformat()+'Z'})
        forecasts.extend(rows)
        sources.append({'url': url, 'rows': len(rows)})
        if day < 31:
            target = datetime(2026, 1, 2) + timedelta(days=day)
            rows, url = fetch('FUELHH', {'settlementDateFrom': target.date().isoformat(), 'settlementDateTo': target.date().isoformat(), 'fuelType': 'WIND'})
            actuals.extend(r for r in rows if r.get('fuelType') == 'WIND')
            sources.append({'url': url, 'rows': len(rows)})
        print(f'Downloaded chunk {day+1}/32', flush=True)
    files = {}
    for name, rows in [('forecasts', forecasts), ('actuals', actuals)]:
        unique = {json.dumps(r, sort_keys=True): r for r in rows}
        payload = json.dumps(list(unique.values()), separators=(',', ':')).encode()
        tmp = DATA / (name + '.tmp')
        tmp.write_bytes(payload)
        tmp.replace(DATA / (name + '.json'))
        files[name] = {'rows': len(unique), 'sha256': hashlib.sha256(payload).hexdigest()}
    (DATA / 'manifest.json').write_text(json.dumps({'retrievedAt': datetime.now(timezone.utc).isoformat(), 'files': files, 'sources': sources}, indent=2))

if __name__ == '__main__':
    main()
