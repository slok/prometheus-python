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

from prometheus.collectors import Summary
from prometheus.registry import Registry
from prometheus.exporter import PrometheusMetricHandler

PORT_NUMBER = 4444


def gather_data(registry):
    """Gathers the metrics"""

    # Get the host name of the machine
    host = socket.gethostname()

    # Create our collectors
    io_metric = Summary("write_file_io_example",
                        "Writing io file in disk example.",
                        {'host': host})

    # register the metric collectors
    registry.register(io_metric)
    chunk = b'\xff'*4000  # 4000 bytes
    filename_path = "/tmp/prometheus_test"
    blocksizes = (100, 10000, 1000000, 100000000)

    # Start gathering metrics every 0.7 seconds
    while True:
        time.sleep(0.7)

        for i in blocksizes:
            time_start = time.time()
            # Action
            with open(filename_path, "wb") as f:
                for _ in range(i // 10000):
                    f.write(chunk)

            io_metric.add({"file": filename_path, "block": i},
                          time.time() - time_start)

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
