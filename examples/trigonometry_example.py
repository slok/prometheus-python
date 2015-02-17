# Set the python path
import inspect
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

import math
import threading
from http.server import HTTPServer
import socket
import time

from prometheus.collectors import Gauge
from prometheus.registry import Registry
from prometheus.exporter import PrometheusMetricHandler

PORT_NUMBER = 4444


def gather_data(registry):
    """Gathers the metrics"""

    # Get the host name of the machine
    host = socket.gethostname()

    # Create our collectors
    trig_metric = Gauge("trigonometry_example",
                        "Various trigonometry examples.",
                        {'host': host})

    # register the metric collectors
    registry.register(trig_metric)

    # Start gathering metrics every second
    counter = 0
    while True:
        time.sleep(1)

        sine = math.sin(math.radians(counter % 360))
        cosine = math.cos(math.radians(counter % 360))
        trig_metric.set({'type': "sine"}, sine)
        trig_metric.set({'type': "cosine"}, cosine)

        counter += 1

if __name__ == "__main__":

    # Create the registry
    registry = Registry()

    # Create the thread that gathers the data while we serve it
    thread = threading.Thread(target=gather_data, args=(registry, ))
    thread.start()

    # Set a server to export (expose to prometheus) the data (in a thread)
    try:
        # We make this to set the registry in the handler
        def handler(*args, **kwargs):
            PrometheusMetricHandler(registry, *args, **kwargs)

        server = HTTPServer(('', PORT_NUMBER), handler)
        server.serve_forever()

    except KeyboardInterrupt:
        server.socket.close()
        thread.join()
