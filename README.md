# prom_twitter_finagle_exporter
prometheus twitter finagle metrics exporter


```bash
./finagle-exporter start --help
Usage: finagle-exporter start [OPTIONS]

Options:
  -s, --service TEXT      service name  [required]
  -u, --url TEXT          url to collect from  [required]
  -p, --port INTEGER      [required]
  -c, --consul-host TEXT
  -e, --exclude TEXT      exclude metrics named
  --help                  Show this message and exit.
```

example 
```bash
$ ./finagle-exporter start \
    --port 9161 \
    --url http://example.com:15277/admin/metrics.json \
    --service nibble
```
