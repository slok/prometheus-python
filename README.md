
Prometheus python client
==================

Python client library for [Prometheus](http://prometheus.io) that can
serve data to prometheus (in text and protobuf formats) and also push data
to a pushgateway.

[![CircleCI](https://circleci.com/gh/slok/prometheus-python.png?style=shield&circle-token=:circle-token)](https://circleci.com/gh/slok/prometheus-python)
[![Coverage Status](https://coveralls.io/repos/slok/prometheus-python/badge.svg?branch=master)](https://coveralls.io/r/slok/prometheus-python?branch=master)



Status
------
Under *heavy* development


Install
-------

    $ pip install prometheus

Usage
-----

### Examples

* [Memory and cpu usage](examples/memory_cpu_usage_example.py)

### Serve data:

    from http.server import HTTPServer
    from prometheus.exporter import PrometheusMetricHandler
    from prometheus.registry import Registry

    registry = Registry()

    def handler(*args, **kwargs):
        PrometheusMetricHandler(registry, *args, **kwargs)

    server = HTTPServer(('', 8888), handler)
    server.serve_forever()

### Push data (to pushgateway)

    TODO

Metrics/Collectors
-------------------

### Counter

    from prometheus.collectors import Counter

    uploads_metric = Counter("file_uploads_total", "File total uploads.")
    uploads_metric.inc({'type': "png", })

### Gauge

    from prometheus.collectors import Gauge

    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.", {'host': host})
    ram_metric.set({'type': "virtual", }, 100)

### Summary

    from prometheus.collectors import Summary

    http_access =  Summary("http_access_time", "HTTP access time", {'time': 'ms'})

    values = [3, 5.2, 13, 4]

    for i in values:
        http_access.add({'time': '/static'}, i)


Labels
------

Labels define the multidimensional magic in prometheus. To add a metric to a collector
you identify with a label for example we have this collector that stores the cosumed
memory:

    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.")

And then we add our RAM user MBs:

    ram_metric.set({'type': "virtual", }, 100)


aplying mutidimensional capacity we can store in the same metric the memory consumed by the
swap of our system too:

    ram_metric.set({'type': "swap", }, 100)


Const labels
------------

When you create a `collector` you can put to than collector constant labels,
these constant labels will apply to all the metrics gathered by that collector
appart from the ones that we put. For example this example without const labels

    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.")
    ram_metric.set({'type': "virtual", 'host': host}, 100)
    ram_metric.set({'type': "swap", 'host': host}, 100)

is the same as this one with const labels:

    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.",  {'host': host})
    ram_metric.set({'type': "virtual", }, 100)
    ram_metric.set({'type': "swap", }, 100)


Tests
-----

    $ pip install -r requirements_test.txt
    $ ./run_tests.sh


TODO
----

* Implement protobuffer
* Implement push


Author
------

[Xabier (slok) Larrakoetxea](http://xlarrakoetxea.org)

License
-------

[See License](/LICENSE)