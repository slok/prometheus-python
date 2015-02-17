from http.server import BaseHTTPRequestHandler


from prometheus.negotiator import Negotiator


class PrometheusMetricHandler(BaseHTTPRequestHandler):

    METRICS_PATH = "/metrics"

    def __init__(self, registry, *args, **kwargs):
        self.registry = registry

        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == self.METRICS_PATH:
            # select formatter (without timestamp)
            formatter = Negotiator.negotiate(self.headers)(False)

            # Response OK
            self.send_response(200)

            # Add headers (type, encoding... and stuff)
            for k, v in formatter.get_headers().items():
                self.send_header(k, v)
            self.end_headers()

            # Get the juice and serve!
            response = formatter.marshall(self.registry)

            # Maybe is protobuf bytes
            if isinstance(response, str):
                response = response.encode("utf8")

            self.wfile.write(response)
            return
