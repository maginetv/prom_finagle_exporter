# prom_twitter_finagle_exporter
prometheus twitter finagle metrics exporter


```bash
./runner start --help
Usage: runner start [OPTIONS]

Options:
  -s, --service TEXT  service name  [required]
  -u, --url TEXT      url to collect from  [required]
  -p, --port INTEGER  [required]
  --help              Show this message and exit.
```

example 
```bash
$ ./runner start \
    --port 9161 \
    --url http://slave-i-135a18af.com1.eu-central-1.tvoli.com:15277/admin/metrics.json \
    --service nibble
```
