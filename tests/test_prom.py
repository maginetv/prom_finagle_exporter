import unittest
from prom_finagle_exporter.prom import TwitterFinagleCollector


class TestTwitterFinagleCollector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = 'http://localhost:9161/metrics'
        cls.service = 'name_of_service'
        cls.exclude_list = ['finagle_exporter_http_response_ko']

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter(self):
        collector = TwitterFinagleCollector(self.url, self.service, exclude=self.exclude_list)
        collector.filter_exclude()
        filtered = collector._get_metric_collect()

        metric_names = [x.get('name') for x in filtered]
        self.assertNotIn(self.exclude_list, metric_names)
