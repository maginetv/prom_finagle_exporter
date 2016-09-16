import socket
import consul
from requests import ConnectionError


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def consul_conn_check(host):
    c = consul.Consul(host=host)
    state = False
    try:
        c.catalog.nodes()
        state = True
    except ConnectionError:
        pass
    finally:
        return state


def register_consul(host, port, service_id=str):
    service_address = get_ip_address()
    conn = consul_conn_check(host)
    if conn:
        c = consul.Consul(host=host)
        result = c.agent.service.register(
            'finagle_exporter',
            service_id=service_id,
            address=service_address,
            port=port,
            check={
                "DeregisterCriticalServiceAfter": "3m",
                "http": "http://{}:{}/health".format(service_address, port),
                "interval": "5s",
                "timeout": "1s"
                }
            )
        return result
    else:
        return False
