from unittest import TestCase
import structlog_extensions
from structlog_extensions.processors import CombinedLogParser
import structlog_extensions.utils as utils
import logging
import sys
import structlog

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)


class TestCombinedLogParser(TestCase):
    def setUp(self):
        self.logparser = CombinedLogParser("gunicorn.access")
        self.logger = logging.Logger("gunicorn.access")
        self.method_name = "warning"
        self.valid_event_dict = {
            'event': '127.0.0.1 - - [05/Feb/2012:17:11:55 +0000] "GET / HTTP/1.1" 200 140 "-" "Mozilla/5.0 (Windows '
                     'NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.5 Safari/535.19"'}
        self.invalid_event_dict = {
            'event': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque bibendum dolor nec arcu '
                     'posuere, eu egestas sapien lacinia. Pellentesque bibendum nulla non tellus finibus aliquet.'}
    def test_has_correct_status_code(self):
        self.assertEqual(200,
                         self.logparser(self.logger, self.method_name,
                                                           self.valid_event_dict)['http.response.status_code'],
                         "Status code not extracted correctly")
    def test_has_correct_host(self):
        self.assertEqual("127.0.0.1",
            self.logparser(self.logger, self.method_name, self.valid_event_dict)['source.ip'],
            "Host not extracted correctly")

    def test_has_correct_timestamp(self):
        self.assertEqual("2012-02-05T17:11:55+00:00",
            self.logparser(self.logger, self.method_name, self.valid_event_dict)['@timestamp'],
            "Timestamp incorrect")

    def test_method_correct(self):
        self.assertEqual("get",
            self.logparser(self.logger, self.method_name, self.valid_event_dict)['http.request.method'],
            "method incorrect")

    def test_url_correct(self):
        self.assertEqual("/",
            self.logparser(self.logger, self.method_name, self.valid_event_dict)[
                'url.original'],
            "url incorrect")

    def http_version_correct(self):
        self.assertEqual("1.1",
            self.logparser(self.logger, self.method_name, self.valid_event_dict)[
                'http.version'],
            "http version incorrect")

    # TODO: Finish off testing correctness of every field, also add asserts for presence of field

    def test_not_a_combined_log(self):
       self.assertNotIn('source.ip',self.logparser(self.logger, self.method_name, self.invalid_event_dict))

    def test_chain_processor(self):
        structlog.configure(
            processors=[
                structlog_extensions.processors.CombinedLogParser("access"),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=False),
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        logger = structlog.get_logger("access")
        logger.warning(
            '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"')


