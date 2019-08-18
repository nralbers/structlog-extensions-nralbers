from unittest import TestCase
from structlog_extensions.processors import CombinedLogParser


class TestCombinedLogParser(TestCase):
    def test_parse_combined_log(self):
        logparser = CombinedLogParser("gunicorn.access")
        logger = object()
        method_name = "warn"
        event_dict = {
            'event': '127.0.0.1 - - [05/Feb/2012:17:11:55 +0000] "GET / HTTP/1.1" 200 140 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.5 Safari/535.19"',
            'logger': 'gunicorn.access', 'level': 'warn'}
        self.assertEqual(logparser.parse_combined_log(logger, method_name, event_dict)['status'], 200, "Status code not extracted correctly")
        self.assertEqual(logparser.parse_combined_log(logger, method_name, event_dict)['host'], "127.0.0.1",
                         "Host not extracted correctly")
