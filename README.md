# prom twitter finagle exporter
prometheus twitter finagle metrics exporter


supported metrics to collect
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

example 
```bash
$ ./finagle-exporter start \
    --port 9161 \
    --url http://example.com:15277/admin/metrics.json \
    --service api
```
