from prometheus_client import REGISTRY, Metric, start_wsgi_server
import click
import json
import requests
import time


metric_collect = [
    {
        'name': 'http_service_requests',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'srv/requests', 'label': {}},
        ]
    },
    {
        'name': 'http_service_success',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'srv/success', 'label': {}},
        ]
    },
    {
        'name': 'http_response_ko',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'response_KO', 'label': {}},
        ]
    },
    {
        'name': 'http_response_ok',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'response_OK', 'label': {}},
        ]
    },
    {
        'name': 'jvm_heap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/heap/max', 'label': {'heap_type': 'max'}},
            {'metric_name': 'jvm/heap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/heap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'jvm_nonheap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/nonheap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/nonheap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'jvm_thread_count',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/thread/count', 'label': {}},
        ]
    },
    {
        'name': 'jvm_mem_current_used',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/mem/current/used', 'label': {}},
        ]
    },
    {
        'name': 'jvm_uptime',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'jvm/uptime', 'label': {}},
        ]
    },
    {
        'name': 'jvm_gc_msec',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/gc/msec', 'label': {}},
        ]
    },
    {
        'name': 'http_request_latency_ms',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'srv/request_latency_ms.sum', 'label': {'latency': 'sum'}},
            {'metric_name': 'srv/request_latency_ms.avg', 'label': {'latency': 'avg'}},
            {'metric_name': 'srv/request_latency_ms.min', 'label': {'latency': 'min'}},
            {'metric_name': 'srv/request_latency_ms.max', 'label': {'latency': 'max'}},
            {'metric_name': 'srv/request_latency_ms.p90', 'label': {'latency': 'p90'}},
            {'metric_name': 'srv/request_latency_ms.p95', 'label': {'latency': 'p95'}},
            {'metric_name': 'srv/request_latency_ms.p99', 'label': {'latency': 'p99'}},
            {'metric_name': 'srv/request_latency_ms.stddev', 'label': {'latency': 'stddev'}},
        ]
    },
]


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
        response = json.loads(requests.get(self._endpoint).content.decode('UTF-8'))
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

        for i in metric_collect:
            metric = Metric(i['name'], i['name'], i['metric_type'])

            for m in i['collect']:
                labels = {}
                labels.update(self._labels)
                labels.update({'original_metric': m['metric_name']})
                if m.get('label'):
                    labels.update(m['label'])
                metric.add_sample(i['name'], value=response[m['metric_name']], labels=labels)

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
