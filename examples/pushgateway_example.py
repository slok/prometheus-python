# Run the pushgatway:
#   docker run  --rm -p 9091:9091 prom/pushgateway
#
# Configure the Pushgateway in prometheus:
#
#   job: {
#     name: "pushgateway"
#     scrape_interval: "1s"
#     target_group: {
#       target: "http://172.17.42.1:9091/metrics"
#     }
#   }
#

# Set the python path
import inspect
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from prometheus.pusher import Pusher
from prometheus.registry import Registry
from prometheus.collectors import Gauge

PUSHGATEWAY_URL = "http://127.0.0.1:9091"

if __name__ == "__main__":
    job_name = "example"
    p = Pusher(job_name, PUSHGATEWAY_URL)
    registry = Registry()
    g = Gauge("up_and_down", "Up and down counter.", {})
    registry.register(g)

    user = input("Hi! enter your username: ")

    while True:
        try:
            n = int(input("Enter a positive or negative number: "))

            g.add({'user': user, }, n)
            # Push to the pushgateway
            p.add(registry)
        except ValueError:
            print("Wrong input")
