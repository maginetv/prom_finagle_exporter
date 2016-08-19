import click
import socket
import falcon
import consul

import prometheus_client
from wsgiref import simple_server

from prom_finagle_exporter.prom import TwitterFinagleCollector


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


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def register_consul(host, port):
    service_address = get_ip_address()
    c = consul.Consul(host=host)
    c.agent.service.register(
        'finagle_exporter',
        address=service_address,
        port=port,
        check={
            "http": "http://{}:{}/health".format(service_address, port),
            "interval": "10s",
            "timeout": "1s"
            }
        )


@click.group(help='')
def cli():
    pass


@click.command()
@click.option('-s', '--service', help='service name', required=True, type=str)
@click.option('-u', '--url', help='url to collect from', required=True, type=str)
@click.option('-p', '--port', help='', required=True, type=int)
@click.option('-c', '--consul-host', help='', default='', type=str)
def start(service, url, port, consul_host):
    if consul_host:
        register_consul(consul_host, port)

    falcon_app(url, service, port=port)


cli.add_command(start)


if __name__ == '__main__':
    cli()
