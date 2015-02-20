
Prometheus python client
==================

Python 3 client library for [Prometheus](http://prometheus.io) that can
serve data to prometheus (in text and protobuf formats) and also push data
to a pushgateway.

[![CircleCI](https://circleci.com/gh/slok/prometheus-python.png?style=shield&circle-token=:circle-token)](https://circleci.com/gh/slok/prometheus-python)
[![Coverage Status](https://coveralls.io/repos/slok/prometheus-python/badge.svg?branch=master)](https://coveralls.io/r/slok/prometheus-python?branch=master)
[![PyPI version](https://badge.fury.io/py/prometheus.svg)](http://badge.fury.io/py/prometheus)

**Table of Contents**

- [Prometheus python client](#)
    - [Status](#)
    - [Install](#)
    - [Why Python 3 and not python 2?](#)
    - [Usage](#)
        - [Serve data](#)
        - [Push data (to pushgateway)](#)
    - [Metrics/Collectors](#)
        - [Counter](#)
        - [Gauge](#)
        - [Summary](#)
    - [Labels](#)
    - [Const labels](#)
    - [Examples](#)
        - [Serve examples](#)
            - [Gauges](#)
            - [Summaries](#)
            - [How to use the examples](#)
        - [PushGateway examples](#)
            - [Gauges](#)
            - [How to use the examples](#)
    - [Tests](#)
    - [TODO](#)
    - [Author](#)
    - [License](#)


Status
------
Under *heavy* development


Install
-------

    $ pip install prometheus


Why Python 3 and not python 2?
-------------------------------

I think that everyone should start adopting the "new" Python version and let
python2 be the old man that every one likes talking to but don't want live be with him.

And the only way doing this is by "forcing people" to use py3.

Also Maintaining code for one version is hard, imagine 2... error prone, slower updates...

So, don't use Python 2 and start using Python 3!

Usage
-----

### Serve data

```python
from http.server import HTTPServer
from prometheus.exporter import PrometheusMetricHandler
from prometheus.registry import Registry

registry = Registry()

def handler(*args, **kwargs):
    PrometheusMetricHandler(registry, *args, **kwargs)

server = HTTPServer(('', 8888), handler)
server.serve_forever()
```

### Push data (to pushgateway)

    TODO

Metrics/Collectors
-------------------

### Counter

```python
from prometheus.collectors import Counter

uploads_metric = Counter("file_uploads_total", "File total uploads.")
uploads_metric.inc({'type': "png", })
```

### Gauge

```python
from prometheus.collectors import Gauge

ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.", {'host': host})
ram_metric.set({'type': "virtual", }, 100)
```

### Summary

```python
from prometheus.collectors import Summary

http_access =  Summary("http_access_time", "HTTP access time", {'time': 'ms'})

values = [3, 5.2, 13, 4]

for i in values:
    http_access.add({'time': '/static'}, i)
```

Labels
------

Labels define the multidimensional magic in prometheus. To add a metric to a collector
you identify with a label for example we have this collector that stores the cosumed
memory:

```python
    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.")
```

And then we add our RAM user MBs:

```python
    ram_metric.set({'type': "virtual", }, 100)
```

aplying mutidimensional capacity we can store in the same metric the memory consumed by the
swap of our system too:

```python
    ram_metric.set({'type': "swap", }, 100)
```

Const labels
------------

When you create a `collector` you can put to than collector constant labels,
these constant labels will apply to all the metrics gathered by that collector
appart from the ones that we put. For example this example without const labels

```python
    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.")
    ram_metric.set({'type': "virtual", 'host': host}, 100)
    ram_metric.set({'type': "swap", 'host': host}, 100)
```

is the same as this one with const labels:

```python
    ram_metric = Gauge("memory_usage_bytes", "Memory usage in bytes.",  {'host': host})
    ram_metric.set({'type': "virtual", }, 100)
    ram_metric.set({'type': "swap", }, 100)
```

Examples
--------

### Serve examples

#### Gauges
* [Memory and cpu usage](examples/memory_cpu_usage_example.py) (Requires psutil)
* [Trigonometry samples](examples/trigonometry_example.py)

#### Summaries
* [Disk write IO timing](examples/timing_write_io_example.py)

#### How to use the examples

First some examples need requirements, install them:

    pip install requirements_test.txt

Now run an example, for example [timing_write_io_example.py](examples/timing_write_io_example.py)

    python ./examples/timing_write_io_example.py

All examples run on port `4444`. You can point prometheus conf like this to
point to one of the examples:

    job: {
      name: "python-client-test"
      scrape_interval: "1s"
      target_group: {
        target: "http://xxx.xxx.xxx.xxx:4444/metrics"
      }
    }

Or you can test the different formats available with curl:

Default (Text 0.0.4):

    curl 'http://127.0.0.1:4444/metrics'


Text (0.0.4):

    curl 'http://127.0.0.1:4444/metrics' -H 'Accept: text/plain; version=0.0.4'


Protobuf debug (0.0.4):

    curl 'http://127.0.0.1:4444/metrics' -H 'Accept: application/vnd.google.protobuf; proto=io.prometheus.client.MetricFamily; encoding=text'

Protobuf (0.0.4):

    curl 'http://127.0.0.1:4444/metrics' -H 'Accept: application/vnd.google.protobuf; proto=io.prometheus.client.MetricFamily; encoding=delimited'


### PushGateway examples

#### Gauges

* [input digits](examples/input_example.py)


#### How to use the examples

First you need to run a gateway, for example with docker:

    docker run  --rm -p 9091:9091 prom/pushgateway

Now configure prometheus to grab the metrics from the push gateway example

    job: {
      name: "pushgateway"
      scrape_interval: "1s"
      target_group: {
        target: "http://172.17.42.1:9091/metrics"
      }
    }

Ready to launch the example:

    python ./examples/input_example.py

As the serve explanation, you can debug de pushgateway serving data by
accessing its URL (in the example: `http://localhost:9091/metrics`) with `Curl`

Tests
-----

    $ pip install -r requirements_test.txt
    $ ./run_tests.sh


TODO
----

* Moaaaar examples
* implement handy utils


Author
------

[Xabier (slok) Larrakoetxea](http://xlarrakoetxea.org)

License
-------

[See License](/LICENSE)