# prom twitter finagle exporter
prometheus twitter finagle metrics exporter. 

### tested with:
* prometheus, version 1.0.1
* consul v0.7.0, v0.6.4
* python 3.5

### consul
when using consul there is a new checks flag used `DeregisterCriticalServiceAfter` set to 3 min. The way this works is after 3 min that the service have been in a critical state the service and linked checks will be removed. This feature is fist added in consul version `0.7.0` the consul registerfunction will still work but there is no de register done. 


### prometheus config
config is done with the assumetion that consul is running on localhost
```yaml
scrape_configs:
  - job_name: 'finagle_exporter'
    scrape_interval: 5s
    consul_sd_configs:
    - server:   'localhost:8500'
      services: ['finagle_exporter']

    relabel_configs:
    - source_labels: ['__meta_consul_service']
      regex:         '(.*)'
      target_label:  'job'
      replacement:   '$1'
    - source_labels: ['__meta_consul_node']
      regex:         '(.*)'
      target_label:  'instance'
      replacement:   '$1'
```


### supported metrics to collect
```bash
srv/requests
srv/success
jvm/heap/max
jvm/heap/used
jvm/heap/committed
jvm/nonheap/used
jvm/nonheap/committed
jvm/thread/count
jvm/mem/current/used
jvm/uptime
jvm/gc/msec
srv/request_latency_ms.sum
srv/request_latency_ms.avg
srv/request_latency_ms.min
srv/request_latency_ms.max
srv/request_latency_ms.p90
srv/request_latency_ms.p95
srv/request_latency_ms.p99
```


output example of prometheus metrics
```bash
# HELP scrape_duration service metric
# TYPE scrape_duration gauge
finigel_scrape_duration_seconds{service="api"} 0.6445069313049316
# HELP finigel_requests finigel_requests
# TYPE finigel_requests counter
finigel_requests{original_metric="srv/requests",service="api"} 529224.0
# HELP finigel_success finigel_success
# TYPE finigel_success counter
finigel_success{original_metric="srv/success",service="api"} 529224.0
# HELP finigel_jvm_heap finigel_jvm_heap
# TYPE finigel_jvm_heap gauge
finigel_jvm_heap{heap_type="max",original_metric="jvm/heap/max",service="api"} 778502144.0
finigel_jvm_heap{heap_type="used",original_metric="jvm/heap/used",service="api"} 380174784.0
finigel_jvm_heap{heap_type="committed",original_metric="jvm/heap/committed",service="api"} 537108480.0
# HELP finigel_jvm_nonheap finigel_jvm_nonheap
# TYPE finigel_jvm_nonheap gauge
finigel_jvm_nonheap{heap_type="used",original_metric="jvm/nonheap/used",service="api"} 102701376.0
finigel_jvm_nonheap{heap_type="committed",original_metric="jvm/nonheap/committed",service="api"} 104574976.0
# HELP finigel_jvm_thread_count finigel_jvm_thread_count
# TYPE finigel_jvm_thread_count gauge
finigel_jvm_thread_count{original_metric="jvm/thread/count",service="api"} 100.0
# HELP finigel_jvm_mem_current_used finigel_jvm_mem_current_used
# TYPE finigel_jvm_mem_current_used gauge
finigel_jvm_mem_current_used{original_metric="jvm/mem/current/used",service="api"} 482876160.0
# HELP finigel_jvm_uptime finigel_jvm_uptime
# TYPE finigel_jvm_uptime counter
finigel_jvm_uptime{original_metric="jvm/uptime",service="api"} 6774247.0
# HELP finigel_jvm_gc_msec finigel_jvm_gc_msec
# TYPE finigel_jvm_gc_msec gauge
finigel_jvm_gc_msec{original_metric="jvm/gc/msec",service="api"} 12164.0
# HELP finigel_request_latency_ms finigel_request_latency_ms
# TYPE finigel_request_latency_ms gauge
finigel_request_latency_ms{latency="sum",original_metric="srv/request_latency_ms.sum",service="api"} 13846.0
finigel_request_latency_ms{latency="avg",original_metric="srv/request_latency_ms.avg",service="api"} 2.95981188542112
finigel_request_latency_ms{latency="min",original_metric="srv/request_latency_ms.min",service="api"} 0.0
finigel_request_latency_ms{latency="max",original_metric="srv/request_latency_ms.max",service="api"} 221.0
finigel_request_latency_ms{latency="p90",original_metric="srv/request_latency_ms.p90",service="api"} 3.0
finigel_request_latency_ms{latency="p95",original_metric="srv/request_latency_ms.p95",service="api"} 4.0
finigel_request_latency_ms{latency="p99",original_metric="srv/request_latency_ms.p99",service="api"} 32.0 
```


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

#### install local
```bash
python3 setup.py install
```

run service
```bash
$ finagle-exporter start \
    --service api \
    --url http://example.com:14056/admin/metrics.json \
    --port 9191 \
    --consul-host 127.0.0.1
```

#### docker build
```bash
$ docker build -t finagle-exporter .
```

run container
```bash
$ docker run -it -p 9191:9191 \
    finagle-exporter start \
        --service api \
        --url http://example.com:14056/admin/metrics.json \
        --port 9191 \
        --consul-host 127.0.0.1
```


### Contributing

Pull requests are very welcome if you feel like you would like to improve
or add any functionality. In order to contribute:

- Fork this repository on GitHub
- Create your own topic branch
- Once finished, submit a pull request

### License

Released under the [Apache 2.0 license](LICENSE).

```
Copyright 2016 Magine AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Author

Alexander Brandstedt (alexander.brandstedt at magine/com)
