import prometheus_client
from prometheus_client import Metric

import falcon
from wsgiref import simple_server

import click
import json
import requests
import time


metric_collect = [
    {
        'name': 'finagle_exporter_http_service_requests',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'srv/requests', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_http_service_success',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'srv/success', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_http_response_ko',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'response_KO', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_http_response_ok',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'response_OK', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_heap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/heap/max', 'label': {'heap_type': 'max'}},
            {'metric_name': 'jvm/heap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/heap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_nonheap',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/nonheap/used', 'label': {'heap_type': 'used'}},
            {'metric_name': 'jvm/nonheap/committed', 'label': {'heap_type': 'committed'}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_thread_count',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/thread/count', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_mem_current_used',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/mem/current/used', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_uptime',
        'metric_type': 'counter',
        'collect': [
            {'metric_name': 'jvm/uptime', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_jvm_gc_msec',
        'metric_type': 'gauge',
        'collect': [
            {'metric_name': 'jvm/gc/msec', 'label': {}},
        ]
    },
    {
        'name': 'finagle_exporter_http_request_latency_ms',
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


class metricHandler:
    def __init__(self, url='', service=''):
        self._service = service
        self._url = url

    def on_get(self, req, resp):
        resp.set_header('Content-Type', prometheus_client.exposition.CONTENT_TYPE_LATEST)
        registry = TwitterFinagleCollector(self._url, self._service)
        collected_metric = prometheus_client.exposition.generate_latest(registry)
        resp.body = collected_metric


class healthHandler:
    def __init__(self):
        pass

    def on_get(self, req, resp):
        resp.body = '{"status": "OK"}'


def falcon_app(url, service, port=9161, addr='0.0.0.0'):
    api = falcon.API()
    api.add_route('/health', healthHandler())
    api.add_route('/', metricHandler(url=url, service=service))
    httpd = simple_server.make_server(addr, port, api)
    httpd.serve_forever()


def announce_consul(host):
    pass


@click.group(help='')
def cli():
    pass


@click.command()
@click.option('-s', '--service', help='service name', required=True, type=str)
@click.option('-u', '--url', help='url to collect from', required=True, type=str)
@click.option('-p', '--port', help='', required=True, type=int)
@click.option('-c', '--consul-host', help='', type=int)
def start(service, url, port, consul_host):
    try:
        falcon_app(url, service, port=port)
    except KeyboardInterrupt:
        print('Stopping')


cli.add_command(start)


if __name__ == '__main__':
    cli()
