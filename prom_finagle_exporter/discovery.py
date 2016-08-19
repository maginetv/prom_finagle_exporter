import socket
import consul


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
