"""Pure analysis functions: no network, no hidden forecast interpolation."""
import math
from datetime import datetime, timedelta, timezone
from statistics import mean

UTC = timezone.utc

def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed.astimezone(UTC)

def quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered)-1)*probability
    lo, hi = math.floor(index), math.ceil(index)
    return ordered[lo] + (ordered[hi]-ordered[lo])*(index-lo)

def metrics(rows):
    paired = [r for r in rows if r['forecast'] is not None and r['actual'] is not None]
    errors = [r['forecast']-r['actual'] for r in paired]
    absolute = [abs(e) for e in errors]
    denominator = sum(r['actual'] for r in paired)
    return {'n':len(paired), 'expected':len(rows), 'coverage':len(paired)/len(rows) if rows else 0,
            'mae':mean(absolute) if errors else None,
            'rmse':math.sqrt(mean(e*e for e in errors)) if errors else None,
            'bias':mean(errors) if errors else None,
            'wape':sum(absolute)/denominator*100 if denominator else None,
            'p90AbsoluteError':quantile(absolute, .9),
            'p90Overforecast':max(0, quantile(errors,.9)) if errors else None,
            'netErrorMWh':sum(errors) if errors else None}

def build_report(forecasts, actuals, decision_date, cutoff='09:00'):
    decision = datetime.fromisoformat(decision_date).replace(tzinfo=UTC)
    if not datetime(2026,1,1,tzinfo=UTC) <= decision < datetime(2026,2,1,tzinfo=UTC):
        raise ValueError('Decision date must be in January 2026')
    hour, minute = map(int, cutoff.split(':'))
    asof = decision.replace(hour=hour,minute=minute)
    delivery = decision + timedelta(days=1)
    selected = {}
    for record in forecasts:
        target, published = timestamp(record['startTime']), timestamp(record['publishTime'])
        value = record.get('generation')
        if not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0:
            continue
        if delivery <= target < delivery+timedelta(days=1) and published < asof:
            previous = selected.get(target)
            if previous is None or published > timestamp(previous['publishTime']):
                selected[target] = record
            elif published == timestamp(previous['publishTime']) and value != previous['generation']:
                raise ValueError('Conflicting forecast values at the same publication timestamp')
    actual_index = {}
    for record in actuals:
        if record.get('fuelType') != 'WIND':
            continue
        target = timestamp(record['startTime'])
        value = record.get('generation')
        if not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0:
            continue
        previous = actual_index.get(target)
        if previous is None or timestamp(record['publishTime']) > timestamp(previous['publishTime']):
            actual_index[target] = record
        elif timestamp(record['publishTime']) == timestamp(previous['publishTime']) and value != previous['generation']:
            raise ValueError('Conflicting actual values at the same publication timestamp')
    rows = []
    for h in range(24):
        target = delivery+timedelta(hours=h)
        record = selected.get(target)
        halves = [actual_index.get(target+timedelta(minutes=m)) for m in (0,30)]
        actual = mean(r['generation'] for r in halves) if all(halves) else None
        forecast = record['generation'] if record else None
        rows.append({'startTime':target.isoformat(),'hour':target.strftime('%H:%M'),
                     'forecast':forecast,'actual':actual,
                     'error':forecast-actual if forecast is not None and actual is not None else None,
                     'publishTime':record['publishTime'] if record else None,
                     'ageHours':(asof-timestamp(record['publishTime'])).total_seconds()/3600 if record else None,
                     'leadHours':(target-timestamp(record['publishTime'])).total_seconds()/3600 if record else None,
                     'actualHalfHours':sum(r is not None for r in halves)})
    available = [r['forecast'] for r in rows if r['forecast'] is not None]
    return {'decisionDate':decision_date, 'deliveryDate':delivery.date().isoformat(),
            'cutoff':asof.isoformat(),'rows':rows,'metrics':metrics(rows),
            'forecastHours':len(available),'forecastMWh':sum(available) if len(available)==24 else None,
            'meanForecast':mean(available) if available else None,
            'maxAgeHours':max((r['ageHours'] for r in rows if r['ageHours'] is not None),default=None)}

def month_report(forecasts, actuals, cutoff):
    days = [build_report(forecasts,actuals,f'2026-01-{day:02d}',cutoff) for day in range(1,32)]
    rows = [row for day in days for row in day['rows']]
    return {'metrics':metrics(rows), 'days':[{'decisionDate':d['decisionDate'],'deliveryDate':d['deliveryDate'],**d['metrics']} for d in days],
            'hours':[{'hour':f'{h:02d}:00',**metrics([r for r in rows if r['hour']==f'{h:02d}:00'])} for h in range(24)]}
