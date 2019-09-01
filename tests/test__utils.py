from unittest import TestCase
import structlog_extensions.utils as utils


class Test_utils(TestCase):
    def test__parse_request_section(self):
        requests = {'get': 'GET /apache_pb.gif HTTP/1.0',
                    'post': 'POST /apache_pb.gif HTTP/1.0',
                    'put': 'PUT /apache_pb.gif HTTP/1.0',
                    'delete': 'DELETE /apache_pb.gif HTTP/1.0'}

        for method, request in requests.items():
            result = utils._parse_request_section(request)
            print(result)
            self.assertEqual(result['method'], method)

        request = "NotAValidRequestString"
        result = utils._parse_request_section(request)
        self.assertNotIn('method', result)

    def test__parse_user_agent_section(self):
        user_agents = {
            'Chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'IE': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
            'Firefox': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Googlebot-Image': 'Googlebot-Image/1.0',
            'Other': 'hjkhsdfjkhjrkf'}

        for agent_name, agent_string in user_agents.items():
            result = utils._parse_user_agent_section(agent_string)
            print(result)
            self.assertEqual(result['user_agent.name'], agent_name)


