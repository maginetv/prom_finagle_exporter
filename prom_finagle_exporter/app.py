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

    # <collect key> <new key>
    metric_keys = {
        'srv/requests': 'http_service_requests',
        'srv/success': 'http_service_success',
        'response_KO': 'http_response_ko',
        'response_OK': 'http_response_ok'
        }
    for k, v in metric_keys.items():
        if data.get(k):
            filtered.append({
                'name': v,
                'value': data.get(k),
                'orginal_metric_name': k,
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
        response_data = json.loads(requests.get(self._endpoint).content.decode('UTF-8'))
        metrics_list = filter_metrics(response_data)

        # Counter metrics
        for i in metrics_list:
            labels = {}
            labels.update(self._labels)
            labels.update({'orginal_metric_name': i['orginal_metric_name']})

            metric = Metric(i['name'], 'scala twitter http service metrics', 'counter')
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
