import re
import unittest

from collectors import Collector, Counter, Gauge
from formats import TextFormat


class TestTextFormat(unittest.TestCase):

    def test_wrong_format(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }

        f = TextFormat()

        c = Collector(**self.data)

        with self.assertRaises(TypeError) as context:
            f.marshall(c)

        self.assertEqual('Not a valid object format', str(context.exception))

    def test_counter_format(self):

        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': None,
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
            "logged_users_total{country=\"ch\",device=\"mobile\"} 654",
            "logged_users_total{country=\"zh\",device=\"desktop\"} 520",
            "logged_users_total{country=\"jp\",device=\"desktop\"} 995",
            "logged_users_total{country=\"de\",device=\"desktop\"} 995",
            "logged_users_total{country=\"pt\",device=\"desktop\"} 995",
            "logged_users_total{country=\"ca\",device=\"desktop\"} 1001",
            "logged_users_total{country=\"sp\",device=\"desktop\"} 520",
            "logged_users_total{country=\"au\",device=\"desktop\"} 520",
            "logged_users_total{country=\"uk\",device=\"desktop\"} 1001",
            "logged_users_total{country=\"py\",device=\"mobile\"} 654",
            "logged_users_total{country=\"us\",device=\"mobile\"} 654",
            "logged_users_total{country=\"ar\",device=\"desktop\"} 1001",
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

    def test_counter_format_with_const_labels(self):

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
            "logged_users_total{app=\"my_app\",country=\"ch\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"zh\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"jp\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"de\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"pt\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"ca\",device=\"desktop\"} 1001",
            "logged_users_total{app=\"my_app\",country=\"sp\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"au\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"uk\",device=\"desktop\"} 1001",
            "logged_users_total{app=\"my_app\",country=\"py\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"us\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"ar\",device=\"desktop\"} 1001",
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
container_cpu_usage_seconds_total{id="cefa0b389a634a0b2f3c2f52ade668d71de75e5775e91297bd65bebe745ba054",name="prometheus",type="user"} 0"""

        data = (
            ({'id': "110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca", 'name': "container-extractor", 'type': "kernel"}, 0),
            ({'id': "110863b5395f7f3476d44e7cb8799f2643abbd385dd544bcc379538ac6ffc5ca", 'name': "container-extractor", 'type': "user"}, 0),
            ({'id': "7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36", 'name': "calendall_db_1", 'type': "kernel"}, 0),
            ({'id': "7c1ae8f404be413a6413d0792123092446f694887f52ae6403356215943d3c36", 'name': "calendall_db_1", 'type': "user"}, 0),
            ({'id': "c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172", 'name': "calendall_web_run_8", 'type': "kernel"}, 0),
            ({'id': "c863b092d1ecdc68f54a6a4ed0d24fe629696be2337ccafb44c279c7c2d1c172", 'name': "calendall_web_run_8", 'type': "user"}, 0),
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
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))

        self.assertEqual(valid_result, result)

    def test_counter_format_with_timestamp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {},
        }
        c = Counter(**self.data)

        counter_data = ({'country': "ch", "device": "mobile"}, 654)

        c.set_value(counter_data[0], counter_data[1])

        result_regex = """# HELP logged_users_total Logged users in the application
# TYPE logged_users_total counter
logged_users_total{country="ch",device="mobile"} 654 \d*(?:.\d*)?$"""

        f_with_ts = TextFormat(True)
        result = f_with_ts.marshall(c)
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))
        self.assertTrue(re.match(result_regex, result))

    def test_single_counter_format_text(self):

        name = "prometheus_dns_sd_lookups_total"
        help_text = "The number of DNS-SD lookups."

        valid_result = """# HELP prometheus_dns_sd_lookups_total The number of DNS-SD lookups.
# TYPE prometheus_dns_sd_lookups_total counter
prometheus_dns_sd_lookups_total 10"""

        data = (
            (None, 10),
        )

        # Create the counter
        c = Counter(name=name, help_text=help_text, const_labels={})

        for i in data:
            c.set_value(i[0], i[1])

        # Select format
        f = TextFormat()

        result = f.marshall(c)
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))

        self.assertEqual(valid_result, result)

    def test_gauge_format(self):

        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {},
        }
        g = Gauge(**self.data)

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
            "# TYPE logged_users_total gauge",
            "logged_users_total{country=\"ch\",device=\"mobile\"} 654",
            "logged_users_total{country=\"zh\",device=\"desktop\"} 520",
            "logged_users_total{country=\"jp\",device=\"desktop\"} 995",
            "logged_users_total{country=\"de\",device=\"desktop\"} 995",
            "logged_users_total{country=\"pt\",device=\"desktop\"} 995",
            "logged_users_total{country=\"ca\",device=\"desktop\"} 1001",
            "logged_users_total{country=\"sp\",device=\"desktop\"} 520",
            "logged_users_total{country=\"au\",device=\"desktop\"} 520",
            "logged_users_total{country=\"uk\",device=\"desktop\"} 1001",
            "logged_users_total{country=\"py\",device=\"mobile\"} 654",
            "logged_users_total{country=\"us\",device=\"mobile\"} 654",
            "logged_users_total{country=\"ar\",device=\"desktop\"} 1001",
        )

        # Add data to the collector
        for i in counter_data:
            g.set_value(i[0], i[1])

        # Select format
        f = TextFormat()
        result = f.marshall(g)

        result = sorted(result)
        valid_result = sorted(valid_result)

        self.assertEqual(valid_result, result)

    def test_gauge_format_with_const_labels(self):

        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }
        g = Gauge(**self.data)

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
            "# TYPE logged_users_total gauge",
            "logged_users_total{app=\"my_app\",country=\"ch\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"zh\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"jp\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"de\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"pt\",device=\"desktop\"} 995",
            "logged_users_total{app=\"my_app\",country=\"ca\",device=\"desktop\"} 1001",
            "logged_users_total{app=\"my_app\",country=\"sp\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"au\",device=\"desktop\"} 520",
            "logged_users_total{app=\"my_app\",country=\"uk\",device=\"desktop\"} 1001",
            "logged_users_total{app=\"my_app\",country=\"py\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"us\",device=\"mobile\"} 654",
            "logged_users_total{app=\"my_app\",country=\"ar\",device=\"desktop\"} 1001",
        )

        # Add data to the collector
        for i in counter_data:
            g.set_value(i[0], i[1])

        # Select format
        f = TextFormat()
        result = f.marshall(g)

        result = sorted(result)
        valid_result = sorted(valid_result)

        self.assertEqual(valid_result, result)

    def test_gauge_format_text(self):

        name = "container_memory_max_usage_bytes"
        help_text = "Maximum memory usage ever recorded in bytes."

        valid_result = """# HELP container_memory_max_usage_bytes Maximum memory usage ever recorded in bytes.
# TYPE container_memory_max_usage_bytes gauge
container_memory_max_usage_bytes{id="4f70875bb57986783064fe958f694c9e225643b0d18e9cde6bdee56d47b7ce76",name="prometheus"} 0
container_memory_max_usage_bytes{id="89042838f24f0ec0aa2a6c93ff44fd3f3e43057d35cfd32de89558112ecb92a0",name="calendall_web_run_3"} 0
container_memory_max_usage_bytes{id="d11c6bc95459822e995fac4d4ae527f6cac442a1896a771dbb307ba276beceb9",name="db"} 0
container_memory_max_usage_bytes{id="e4260cc9dca3e4e50ad2bffb0ec7432442197f135023ab629fe3576485cc65dd",name="container-extractor"} 0
container_memory_max_usage_bytes{id="f30d1caaa142b1688a0684ed744fcae6d202a36877617b985e20a5d33801b311",name="calendall_db_1"} 0
container_memory_max_usage_bytes{id="f835d921ffaf332f8d88ef5231ba149e389a2f37276f081878d6f982ef89a981",name="cocky_fermat"} 0"""

        data = (
            ({'id': "4f70875bb57986783064fe958f694c9e225643b0d18e9cde6bdee56d47b7ce76", 'name': "prometheus"}, 0),
            ({'id': "89042838f24f0ec0aa2a6c93ff44fd3f3e43057d35cfd32de89558112ecb92a0", 'name': "calendall_web_run_3"}, 0),
            ({'id': "d11c6bc95459822e995fac4d4ae527f6cac442a1896a771dbb307ba276beceb9", 'name': "db"}, 0),
            ({'id': "e4260cc9dca3e4e50ad2bffb0ec7432442197f135023ab629fe3576485cc65dd", 'name': "container-extractor"}, 0),
            ({'id': "f30d1caaa142b1688a0684ed744fcae6d202a36877617b985e20a5d33801b311", 'name': "calendall_db_1"}, 0),
            ({'id': "f835d921ffaf332f8d88ef5231ba149e389a2f37276f081878d6f982ef89a981", 'name': "cocky_fermat"}, 0),
        )

        # Create the counter
        g = Gauge(name=name, help_text=help_text, const_labels={})

        for i in data:
            g.set_value(i[0], i[1])

        # Select format
        f = TextFormat()

        result = f.marshall(g)
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))

        self.assertEqual(valid_result, result)

    def test_gauge_format_with_timestamp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {},
        }
        g = Gauge(**self.data)

        counter_data = ({'country': "ch", "device": "mobile"}, 654)

        g.set_value(counter_data[0], counter_data[1])

        result_regex = """# HELP logged_users_total Logged users in the application
# TYPE logged_users_total gauge
logged_users_total{country="ch",device="mobile"} 654 \d*(?:.\d*)?$"""

        f_with_ts = TextFormat(True)
        result = f_with_ts.marshall(g)
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))
        self.assertTrue(re.match(result_regex, result))

    def test_single_gauge_format_text(self):

        name = "prometheus_local_storage_indexing_queue_capacity"
        help_text = "The capacity of the indexing queue."

        valid_result = """# HELP prometheus_local_storage_indexing_queue_capacity The capacity of the indexing queue.
# TYPE prometheus_local_storage_indexing_queue_capacity gauge
prometheus_local_storage_indexing_queue_capacity 16384"""

        data = (
            (None, 16384),
        )

        # Create the counter
        g = Gauge(name=name, help_text=help_text, const_labels={})

        for i in data:
            g.set_value(i[0], i[1])

        # Select format
        f = TextFormat()

        result = f.marshall(g)
        result = TextFormat.LINE_SEPARATOR_FMT.join(sorted(result))

        self.assertEqual(valid_result, result)
