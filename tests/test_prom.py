import unittest
from prom_finagle_exporter.prom import TwitterFinagleCollector


class TestTwitterFinagleCollector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = 'http://localhost:9191/metrics'
        cls.service = 'name_of_service'
        cls.exclude_list = ['finagle_exporter_http_response_ko']
        cls.collector = TwitterFinagleCollector(
            cls.url,
            cls.service,
            exclude=cls.exclude_list
            )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter(self):
        self.collector.filter_exclude()
        filtered = self.collector._get_metric_collect()

        metric_names = [x.get('name') for x in filtered]
        self.assertNotIn(self.exclude_list, metric_names)

    def test_gen_response_metrics_dict(self):
        resp_data = {
            "srv/requests": 1,
            "srv/foo": 2,
            "srv/bar": 3,
            }
        result = self.collector._gen_response_metrics_dict(resp_data)
        print(result)
        self.assertEqual(result, [{'srv/requests': 1}])

    def test_gen_response_metrics_dict_no_match(self):
        resp_data = {
            "srv/foo": 2,
            "srv/bar": 3,
            }
        result = self.collector._gen_response_metrics_dict(resp_data)
        self.assertFalse(result)
