import csv
import gzip
import io
import json
from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from backend.analysis import build_report, month_report

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title='Windward API',version='1.0.0',description='January 2026 Elexon wind decision replay. Forecast cutoffs are exclusive.')

@lru_cache(maxsize=1)
def snapshot():
    try:
        def read(name):
            path = ROOT/'data'/f'{name}.json'
            payload = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes())
            return json.loads(payload)
        return tuple(read(name) for name in ('forecasts','actuals','manifest'))
    except (OSError,ValueError) as error:
        raise HTTPException(503,'Snapshot unavailable. Run python scripts/ingest.py.') from error

@app.get('/api/health')
def health():
    forecasts, actuals, manifest = snapshot()
    return {'status':'ok','forecasts':len(forecasts),'actuals':len(actuals),'retrievedAt':manifest['retrievedAt']}

@app.get('/api/provenance')
def provenance():
    return snapshot()[2]

def report(date, cutoff):
    try:
        f,a,_ = snapshot()
        return build_report(f,a,date,cutoff)
    except ValueError as error:
        raise HTTPException(422,str(error)) from error

@app.get('/api/day')
def day(date: str = Query('2026-01-15',pattern=r'^2026-01-(0[1-9]|[12][0-9]|3[01])$'), cutoff: str = Query('09:00',pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')):
    return report(date,cutoff)

@lru_cache(maxsize=64)
def cached_month(cutoff):
    f,a,_ = snapshot()
    return month_report(f,a,cutoff)

@app.get('/api/month')
def month(cutoff: str = Query('09:00',pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')):
    return cached_month(cutoff)

@app.get('/api/export')
def export(date: str = Query('2026-01-15',pattern=r'^2026-01-(0[1-9]|[12][0-9]|3[01])$'), cutoff: str = Query('09:00',pattern=r'^([01][0-9]|2[0-3]):[0-5][0-9]$')):
    data = report(date,cutoff)
    stream = io.StringIO()
    fields = ['decisionDate','cutoff','startTime','forecast','actual','error','publishTime','ageHours','leadHours','actualHalfHours']
    writer = csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
    writer.writeheader()
    for row in data['rows']:
        writer.writerow({'decisionDate':date,'cutoff':data['cutoff'],**row})
    return Response(stream.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="windward-{date}.csv"'})

dist = ROOT/'frontend'/'dist'
if dist.exists():
    app.mount('/',StaticFiles(directory=dist,html=True),name='frontend')
