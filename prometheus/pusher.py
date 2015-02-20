from urllib.parse import urljoin

import requests

from prometheus.formats import ProtobufFormat


# TODO: Fire and forget pushes
class Pusher(object):
    """ This class is used to push a registry to a pushgateway"""

    PATH = "/metrics/jobs/{0}"
    INSTANCE_PATH = "/metrics/jobs/{0}/instances/{1}"

    def __init__(self, job_name, addr, instance_name=None):
        self.job_name = job_name
        self.instance_name = instance_name
        self.addr = addr

        # push format
        self.formatter = ProtobufFormat()
        self.headers = self.formatter.get_headers()

        # Set paths
        if instance_name:
            self.path = urljoin(self.addr, self.__class__.INSTANCE_PATH).format(
                job_name, instance_name)
        else:
            self.path = urljoin(self.addr, self.__class__.PATH).format(job_name)

    def add(self, registry):
        """ Add works like replace, but only previously pushed metrics with the
            same name (and the same job and instance) will be replaced.
            (It uses HTTP method 'POST' to push to the Pushgateway.)
        """
        # POST
        payload = self.formatter.marshall(registry)
        r = requests.post(self.path, data=payload, headers=self.headers)

    def replace(self, registry):
        """ Push triggers a metric collection and pushes all collected metrics
            to the Pushgateway specified by addr
            Note that all previously pushed metrics with the same job and
            instance will be replaced with the metrics pushed by this call.
            (It uses HTTP method 'PUT' to push to the Pushgateway.)
        """
        # PUT
        payload = self.formatter.marshall(registry)
        r = requests.put(self.path, data=payload, headers=self.headers)

    def delete(self, registry):
        # DELETE
        payload = self.formatter.marshall(registry)
        r = requests.delete(self.path, data=payload, headers=self.headers)
