from unittest import TestCase
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
        self.assertEqual(self.logparser.parse_combined_log(self.logger, self.method_name,
                                                           self.valid_event_dict)['http.response.status_code'], 200,
                         "Status code not extracted correctly")
    def test_has_correct_host(self):
        self.assertEqual(
            self.logparser.parse_combined_log(self.logger, self.method_name, self.valid_event_dict)['source.ip'],
            "127.0.0.1",
            "Host not extracted correctly")

    def test_has_correct_timestamp(self):
        self.assertEqual(
            self.logparser.parse_combined_log(self.logger, self.method_name, self.valid_event_dict)['@timestamp'],
            "05/Feb/2012:17:11:55 +0000",
            "Timestamp incorrect")

    def test_method_correct(self):
        self.assertEqual(
            self.logparser.parse_combined_log(self.logger, self.method_name, self.valid_event_dict)['http.request.method'],
            "get",
            "method incorrect")

    def test_url_correct(self):
        self.assertEqual(
            self.logparser.parse_combined_log(self.logger, self.method_name, self.valid_event_dict)[
                'url.original'],
            "/",
            "url incorrect")

    def http_version_correct(self):
        self.assertEqual(
            self.logparser.parse_combined_log(self.logger, self.method_name, self.valid_event_dict)[
                'http.version'],
            "1.1",
            "http version incorrect")

    # TODO: Finish off testing correctness of every field, also add asserts for presence of field

    def test_not_a_combined_log(self):
       self.assertNotIn('source.ip',self.logparser.parse_combined_log(self.logger, self.method_name, self.invalid_event_dict))

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
        logger.warning(
            '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"')

    def test__parse_user_agent_section(self):
        user_agents = {'Chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
                       'IE': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
                       'Firefox': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
                       'Googlebot-Image': 'Googlebot-Image/1.0',
                       'Other': 'hjkhsdfjkhjrkf'}

        for agent_name, agent_string in user_agents.items():
            result = utils._parse_user_agent_section(agent_string)
            print(result)
            self.assertEqual(result['user_agent.name'], agent_name)

    def test__parse_request_section(self):
        requests = {'get': 'GET /apache_pb.gif HTTP/1.0',
                    'post': 'POST /apache_pb.gif HTTP/1.0',
                    'put': 'PUT /apache_pb.gif HTTP/1.0',
                    'delete': 'DELETE /apache_pb.gif HTTP/1.0'}

        for method,request in requests.items():
            result=utils._parse_request_section(request)
            print(result)
            self.assertEqual(result['method'],method)

        request = "NotAValidRequestString"
        result = utils._parse_request_section(request)
        self.assertNotIn('method',result)
