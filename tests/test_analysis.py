import unittest
from backend.analysis import build_report, metrics, quantile

def forecast(published, value, target='2026-01-02T00:00:00Z'):
    return {'startTime':target,'publishTime':published,'generation':value}

def actual(target,value,fuel='WIND'):
    return {'startTime':target,'publishTime':'2026-01-03T00:00:00Z','generation':value,'fuelType':fuel}

class AnalysisTests(unittest.TestCase):
    def test_cutoff_excludes_equal_and_future(self):
        f=[forecast('2026-01-01T08:30:00Z',100),forecast('2026-01-01T09:00:00Z',200),forecast('2026-01-01T12:00:00Z',300)]
        self.assertEqual(build_report(f,[],'2026-01-01')['rows'][0]['forecast'],100)

    def test_hourly_actual_is_mean_and_filters_fuel(self):
        a=[actual('2026-01-02T00:00:00Z',80),actual('2026-01-02T00:30:00Z',120),actual('2026-01-02T00:00:00Z',999,'CCGT')]
        r=build_report([forecast('2026-01-01T08:00:00Z',150)],a,'2026-01-01')
        self.assertEqual(r['rows'][0]['actual'],100)
        self.assertEqual(r['metrics']['bias'],50)
        self.assertEqual(r['metrics']['netErrorMWh'],50)

    def test_missing_half_hour_not_zero(self):
        r=build_report([forecast('2026-01-01T08:00:00Z',100)],[actual('2026-01-02T00:00:00Z',0)],'2026-01-01')
        self.assertIsNone(r['rows'][0]['actual'])
        self.assertEqual(r['metrics']['n'],0)
        self.assertIsNone(r['forecastMWh'])

    def test_boundary_includes_february_delivery(self):
        r=build_report([],[],'2026-01-31')
        self.assertEqual(r['deliveryDate'],'2026-02-01')
        self.assertEqual(len(r['rows']),24)

    def test_duplicate_conflict_rejected(self):
        with self.assertRaises(ValueError):
            build_report([forecast('2026-01-01T08:00:00Z',1),forecast('2026-01-01T08:00:00Z',2)],[],'2026-01-01')

    def test_zero_actual_has_no_percentage(self):
        m=metrics([{'forecast':10,'actual':0}])
        self.assertEqual(m['mae'],10)
        self.assertIsNone(m['wape'])

    def test_known_metrics(self):
        m=metrics([{'forecast':120,'actual':100},{'forecast':80,'actual':100}])
        self.assertEqual((m['mae'],m['rmse'],m['bias'],m['wape']),(20,20,0,20))
        self.assertEqual(quantile([0,10],.9),9)

    def test_latest_is_independent_of_input_order(self):
        f=[forecast('2026-01-01T08:00:00Z',30),forecast('2026-01-01T07:00:00Z',20)]
        self.assertEqual(build_report(f,[],'2026-01-01')['rows'][0]['forecast'],30)

    def test_outside_decision_scope_rejected(self):
        with self.assertRaises(ValueError):
            build_report([],[],'2026-02-01')

if __name__=='__main__':
    unittest.main()
