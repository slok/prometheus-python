import unittest

from collectors import Counter
from formats import TextFormat


class TestTextFormat(unittest.TestCase):

    def test_counter_format(self):

        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }
        c = Counter(**self.data)

        counter_data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
            ({'country': "zh", "device": "desktop"}, 520),
            ({'country': "ch", "device": "mobile"}, 654),
            ({'country': "ca", "device": "desktop"}, 1001),
            ({'country': "jp", "device": "desktop"}, 995),
            ({'country': "au", "device": "desktop"}, 520),
            ({'country': "py", "device": "mobile"}, 654),
            ({'country': "ar", "device": "desktop"}, 1001),
            ({'country': "pt", "device": "desktop"}, 995),
        )

        valid_result = (
            "# HELP logged_users_total Logged users in the application",
            "# TYPE logged_users_total counter",
            "logged_users_total{country=\"ch\", device=\"mobile\"} 654",
            "logged_users_total{country=\"zh\", device=\"desktop\"} 520",
            "logged_users_total{country=\"jp\", device=\"desktop\"} 995",
            "logged_users_total{country=\"de\", device=\"desktop\"} 995",
            "logged_users_total{country=\"pt\", device=\"desktop\"} 995",
            "logged_users_total{country=\"ca\", device=\"desktop\"} 1001",
            "logged_users_total{country=\"sp\", device=\"desktop\"} 520",
            "logged_users_total{country=\"au\", device=\"desktop\"} 520",
            "logged_users_total{country=\"uk\", device=\"desktop\"} 1001",
            "logged_users_total{country=\"py\", device=\"mobile\"} 654",
            "logged_users_total{country=\"us\", device=\"mobile\"} 654",
            "logged_users_total{country=\"ar\", device=\"desktop\"} 1001",
        )

        # Add data to the collector
        for i in counter_data:
            c.set_value(i[0], i[1])

        # Select format
        f = TextFormat()
        result = f.marshall(c)

        result = sorted(result)
        valid_result = sorted(valid_result)

        self.assertEqual(valid_result, result)

    def test_counter_format_text(self):

        name = "container_cpu_usage_seconds_total"
        help_text = "Total seconds of cpu time consumed."

        valid_result = """# HELP container_cpu_usage_seconds_total Total seconds of cpu time consumed.
# TYPE container_cpu_usage_seconds_total counter
container_cpu_usage_seconds_total{id="110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca",name="container-extractor",type="kernel"} 0
container_cpu_usage_seconds_total{id="110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca",name="container-extractor",type="user"} 0
container_cpu_usage_seconds_total{id="7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36",name="calendall_db_1",type="kernel"} 0
container_cpu_usage_seconds_total{id="7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36",name="calendall_db_1",type="user"} 0
container_cpu_usage_seconds_total{id="c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172",name="calendall_web_run_8",type="kernel"} 0
container_cpu_usage_seconds_total{id="c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172",name="calendall_web_run_8",type="user"} 0
container_cpu_usage_seconds_total{id="cefa0b389a634a0b2f3c2f52ade668d71de75e5775e91297bd65bebe745ba054",name="prometheus",type="kernel"} 0
container_cpu_usage_seconds_total{id="cefa0b389a634a0b2f3c2f52ade668d71de75e5775e91297bd65bebe745ba054",name="prometheus",type="user"} 0
        """

        data = (
            ({'id': "110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca", 'name': "container-extractor", 'type': "kernel"}, 0),
            ({'id': "110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca", 'name': "container-extractor", 'type': "user"}, 0),
            ({'id': "7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36", 'name': "calendall_db_1", 'type': "kernel"}, 0),
            ({'id': "7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36", 'name': "calendall_db_1", 'type': "user"}, 0),
            ({'id': "c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172", 'name': "calendall_web_run_8", 'type': "kernel"}, 0),
            ({'id': "c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172", 'name': "calendall_web_run_8", 'type': "kernel"}, 0),
            ({'id': "cefa0b389a634a0b2f3c2f52ade668d71de75e5775e91297bd65bebe745ba054", 'name': "prometheus", 'type': "kernel"}, 0),
            ({'id': "cefa0b389a634a0b2f3c2f52ade668d71de75e5775e91297bd65bebe745ba054", 'name': "prometheus", 'type': "user"}, 0),
        )

        # Create the counter
        c = Counter(name=name, help_text=help_text, const_labels={})

        for i in data:
            c.set_value(i[0], i[1])

        # Select format
        f = TextFormat()

        result = f.marshall(c)
        result = sorted(result)

        self.assertEqual(valid_result, result)

#    def test_counter_format_with_timestamp(self):
#        pass
