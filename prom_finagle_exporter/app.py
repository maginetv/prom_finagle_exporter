from prometheus_client import REGISTRY, Metric, start_wsgi_server
import click
import json
import requests
import time


"""
    srv/request_latency_ms.sum: 1381,
    srv/request_latency_ms.avg: 1.8738127544097694,
    srv/request_latency_ms.min: 0,
    srv/request_latency_ms.max: 53,
    srv/request_latency_ms.stddev: 3.398711661520411,
    srv/request_latency_ms.p90: 5,
    srv/request_latency_ms.p95: 9,
    srv/request_latency_ms.p99: 12,
    srv/requests
    srv/success
"""


def filter_metrics(data):
    filtered = []

    metric_keys_matching = [
        {'current': 'srv/requests', 'name': 'http_service_requests', 'metric_type': 'counter', 'label': {}},
        {'current': 'srv/success', 'name': 'http_service_success', 'metric_type': 'counter', 'label': {}},

        {'current': 'response_KO', 'name': 'http_response_ko', 'metric_type': 'counter', 'label': {}},
        {'current': 'response_OK', 'name': 'http_response_ok', 'metric_type': 'counter', 'label': {}},

        {'current': 'jvm/heap/max', 'name': 'jvm_heap', 'metric_type': 'gauge',
            'label': {'heap_type': 'max'}},
        {'current': 'jvm/heap/used', 'name': 'jvm_heap', 'metric_type': 'gauge',
            'label': {'heap_type': 'used'}},
        {'current': 'jvm/heap/committed', 'name': 'jvm_heap', 'metric_type': 'gauge',
            'label': {'heap_type': 'committed'}},

        {'current': 'jvm/nonheap/used', 'name': 'jvm_nonheap', 'metric_type': 'gauge',
            'label': {'heap_type': 'used'}},
        {'current': 'jvm/nonheap/committed', 'name': 'jvm_nonheap', 'metric_type': 'gauge',
            'label': {'heap_type': 'committed'}},

        {'current': 'jvm/thread/count', 'name': 'jvm_thread_count', 'metric_type': 'gauge', 'label': {}},
        {'current': 'jvm/mem/current/used', 'name': 'jvm_mem_current_used', 'metric_type': 'gauge', 'label': {}},
        {'current': 'jvm/uptime', 'name': 'jvm_uptime', 'metric_type': 'counter', 'label': {}},
        {'current': 'jvm/gc/msec', 'name': 'jvm_gc_msec', 'metric_type': 'gauge', 'label': {}},

        {'current': 'srv/request_latency_ms.sum', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'sum'}},
        {'current': 'srv/request_latency_ms.avg', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'avg'}},
        {'current': 'srv/request_latency_ms.min', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'min'}},
        {'current': 'srv/request_latency_ms.max', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'max'}},
        {'current': 'srv/request_latency_ms.p90', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'p90'}},
        {'current': 'srv/request_latency_ms.p95', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'p95'}},
        {'current': 'srv/request_latency_ms.p99', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'p99'}},
        {'current': 'srv/request_latency_ms.stddev', 'name': 'request_latency_ms', 'metric_type': 'gauge',
            'label': {'latency': 'stddev'}},
        ]

    for metric in metric_keys_matching:
        if data.get(metric.get('current')):
            filtered.append({
                'name': metric.get('name'),
                'value': data.get(metric['current']),
                'orginal_metric_name': metric['current'],
                'metric_type': metric['metric_type'],
                'label': metric['label']
                })

    return filtered


class TwitterFinagleCollector(object):
    def __init__(self, endpoint, service):
        self._endpoint = endpoint
        self._service = service
        self._labels = {}
        self._set_labels()

    def _set_labels(self):
        self._labels.update({'service': self._service, 'source_type': 'finagle_server'})

    def collect(self):
        time_start = time.time()
        response_data = json.loads(requests.get(self._endpoint).content.decode('UTF-8'))
        metrics_list = filter_metrics(response_data)
        time_stop = time.time()

        scrape_duration_seconds = (time_stop - time_start)
        time_labels = {}
        time_labels.update(self._labels)
        time_metric = Metric('scrape_duration', 'service metric', 'gauge')
        time_metric.add_sample(
            'finagle_exporter_scrape_duration_seconds',
            value=scrape_duration_seconds,
            labels=time_labels
            )
        yield time_metric

        # Counter metrics
        for i in metrics_list:
            labels = {}
            labels.update(self._labels)
            labels.update({'orginal_metric_name': i['orginal_metric_name']})
            if i.get('label'):
                labels.update(i['label'])

            metric = Metric(i['name'], '', i['metric_type'])
            metric.add_sample(i['name'], value=i['value'], labels=labels)

            yield metric


@click.group(help='')
def cli():
    pass


@click.command()
@click.option('-s', '--service', help='service name', required=True, type=str)
@click.option('-u', '--url', help='url to collect from', required=True, type=str)
@click.option('-p', '--port', help='', required=True, type=int)
def start(service, url, port):
    try:
        REGISTRY.register(TwitterFinagleCollector(url, service))
        start_wsgi_server(port, '0.0.0.0')

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping')


cli.add_command(start)


if __name__ == '__main__':
    cli()
