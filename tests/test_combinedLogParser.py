from unittest import TestCase
from structlog_extensions.processors import CombinedLogParser
import logging
import sys
import structlog



logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

class TestCombinedLogParser(TestCase):
    def test_parse_combined_log(self):
        logparser = CombinedLogParser("gunicorn.access")
        logger = logging.Logger("gunicorn.access")
        method_name = "warning"
        event_dict = {
            'event': '127.0.0.1 - - [05/Feb/2012:17:11:55 +0000] "GET / HTTP/1.1" 200 140 "-" "Mozilla/5.0 (Windows '
                     'NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.5 Safari/535.19"'}
        self.assertEqual(logparser.parse_combined_log(logger, method_name, event_dict)['status'], 200,
                         "Status code not extracted correctly")
        self.assertEqual(logparser.parse_combined_log(logger, method_name, event_dict)['host'], "127.0.0.1",
                         "Host not extracted correctly")

    def test_chain_processor(self):
        logparser = CombinedLogParser("access")
        structlog.configure(
            processors=[
                logparser.parse_combined_log,
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
        logger.warning('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"')