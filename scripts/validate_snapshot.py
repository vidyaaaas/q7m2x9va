"""Checks provenance, grid resolution, paired coverage and no-lookahead invariants."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.analysis import build_report, month_report, timestamp

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'data/manifest.json').read_text())
for name,meta in manifest['files'].items():
    assert hashlib.sha256((root/f'data/{name}.json').read_bytes()).hexdigest()==meta['sha256']
f=json.loads((root/'data/forecasts.json').read_text())
a=json.loads((root/'data/actuals.json').read_text())
assert all(timestamp(r['startTime']).minute==0 for r in f), 'Forecast resolution changed: revisit alignment'
assert all(timestamp(r['startTime']).minute in (0,30) and r['fuelType']=='WIND' for r in a)
results={}
for cutoff in ['09:00','09:20','15:00','15:30']:
    month=month_report(f,a,cutoff)
    assert month['metrics']['n']==744, 'Incomplete paired snapshot'
    for day in range(1,32):
        r=build_report(f,a,f'2026-01-{day:02d}',cutoff)
        assert all(timestamp(row['publishTime'])<timestamp(r['cutoff']) for row in r['rows'])
    results[cutoff]=month['metrics']
(root/'docs/validation-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
