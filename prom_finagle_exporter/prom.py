from prometheus_client import Metric

import json
import requests
import time


metric_collect = [
    {
        'name': 'finigel_requests',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'srv/requests', 'label': {}},
        ]
    },
    {
        'name': 'finigel_jvm_heap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/heap/max', 'label': {'heap_type': 'max'}},
            {'metric_name': 'jvm/heap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/heap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'finigel_jvm_nonheap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/nonheap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/nonheap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'finigel_jvm_thread_count',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/thread/count', 'label': {}},
        ]
    },
    {
        'name': 'finigel_jvm_mem_current_used',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/mem/current/used', 'label': {}},
        ]
    },
    {
        'name': 'finigel_jvm_uptime',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'jvm/uptime', 'label': {}},
        ]
    },
    {
        'name': 'finigel_jvm_gc_msec',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/gc/msec', 'label': {}},
        ]
    },
    {
        'name': 'finigel_request_latency_ms',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'srv/request_latency_ms.sum', 'label': {'latency': 'sum'}},
            {'metric_name': 'srv/request_latency_ms.avg', 'label': {'latency': 'avg'}},
            {'metric_name': 'srv/request_latency_ms.min', 'label': {'latency': 'min'}},
            {'metric_name': 'srv/request_latency_ms.max', 'label': {'latency': 'max'}},
            {'metric_name': 'srv/request_latency_ms.p90', 'label': {'latency': 'p90'}},
            {'metric_name': 'srv/request_latency_ms.p95', 'label': {'latency': 'p95'}},
            {'metric_name': 'srv/request_latency_ms.p99', 'label': {'latency': 'p99'}},
        ]
    },
]


class TwitterFinagleCollector(object):
    def __init__(self, endpoint, service, exclude=list):
        self._endpoint = endpoint
        self._service = service
        self._labels = {}
        self._set_labels()
        self._exclude = exclude
        self._metric_collect = metric_collect

    def _set_labels(self):
        self._labels.update({'service': self._service})

    def filter_exclude(self):
        self._metric_collect = list(
            filter(lambda x: x.get('name') not in self._exclude, self._metric_collect)
            )

    def _get_metric_collect(self):
        return self._metric_collect

    def _get_metrics(self):
        response = requests.get(self._endpoint)
        response_data = {}
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content.decode('UTF-8'))
            except ValueError:
                pass
        return response_data

    def _get_metrics_keys(self):
        metric_keys = []
        for i in self._metric_collect:
            for x in i['collect']:
                metric_keys.append(x['metric_name'])
        return metric_keys

    def _gen_response_metrics_dict(self, response_data):
        return [{k: v} for (k, v) in response_data.items() if k in self._get_metrics_keys()]

    def collect(self):
        time_start = time.time()
        response = self._get_metrics()
        time_stop = time.time()

        scrape_duration_seconds = (time_stop - time_start)
        time_labels = {}
        time_labels.update(self._labels)
        time_metric = Metric('scrape_duration', 'service metric', 'gauge')
        time_metric.add_sample(
            'finigel_scrape_duration_seconds',
            value=scrape_duration_seconds,
            labels=time_labels
            )
        yield time_metric

        if self._exclude:
            self.filter_exclude()

        for i in self._metric_collect:
            metric = Metric(i['name'], i['name'], i['metric_type'])

            for m in i['collect']:
                labels = {}
                labels.update(self._labels)
                labels.update({'original_metric': m['metric_name']})
                if m.get('label'):
                    labels.update(m['label'])
                try:
                    metric.add_sample(
                        i['name'],
                        value=response[m['metric_name']],
                        labels=labels
                        )
                except KeyError:
                    pass
            if metric.samples:
                yield metric
            else:
                pass
