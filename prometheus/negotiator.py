from formats import TextFormat


class Negotiator(object):
    """ Negotiator selects the best format based on request header
    """

    FALLBACK = TextFormat
    TEXT = {
        'default': ('text/plain',),
        '0.0.4': ('text/plain',
                  'version=0.0.4'),

    }
    PROTOBUF = {
        "default": ("application/vnd.google.protobuf",
                    "proto=io.prometheus.client.MetricFamily",
                    "encoding=delimited")
    }

    @classmethod
    def negotiate(cls, headers):
        """ Process headers dict to return the format class
            (not the instance)
        """
        # set lower keys
        headers = {k.lower(): v for k, v in headers.items()}

        accept = headers.get('accept', "*/*")

        parsed_accept = accept.split(";")
        parsed_accept = [i.strip() for i in parsed_accept]

        # Protobuffer (only one version)
        if all([i in parsed_accept for i in cls.PROTOBUF['default']]):
            raise NotImplementedError()
        # Text 0.0.4
        elif all([i in parsed_accept for i in cls.TEXT['0.0.4']]):
            return TextFormat
        # Text (Default)
        elif all([i in parsed_accept for i in cls.TEXT['default']]):
            return TextFormat
        # Default
        else:
            return cls.FALLBACK
