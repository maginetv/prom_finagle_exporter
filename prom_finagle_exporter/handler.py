import falcon

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
