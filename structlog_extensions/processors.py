import re
from user_agents import parse
"""
structlog_extensions.processors 

This module contains processors for structlog.
"""

_ecs_field_mappings = {'host':'source.ip',
                       'user': 'user.name',
                       'event': 'event.original',
                       'method': 'http.request.method',
                       'referrer': 'http.request.referrer',
                       'size': 'http.response.body.bytes',
                       'status': 'http.response.status_code',
                       'time': '@timestamp',
                       'url': 'url.original',
                       'version': 'http.version'}

class CombinedLogParser:
    """
    Parses Apache combined log style entries in the event field into separate fields using
    `Elastic Common Schema <https://www.elastic.co/guide/en/ecs/current/ecs-field-reference.html>`_ field names.

    Attributes:
        target_logger (str): Name of the logger object that is logging combined log output.

    Example:
        Creating and using a parser instance with structlog:

        .. code-block:: python

            from structlog_extensions.processors import CombinedLogParser
            import structlog
            import logging

            logparser = CombinedLogParser('access')

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




    """
    def __init__(self, target_logger):
        self.target_logger = target_logger

    def parse_combined_log(self, logger, method_name, event_dict):
        """
        Filter function to parse combined logs.

        Add to the structlog processors list or the stdlib logger
        foreign_pre_chain list to apply splitting of combined log entries to log entries.

        Example:

            .. code-block:: python

                structlog.configure(
                    processors=[
                        logparser.parse_combined_log,  # pass function as a list item. NOTE! no ()
                        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                    ],
                    logger_factory=structlog.stdlib.LoggerFactory(),
                )

        Args:
            logger(logging.Logger): Logger object passed by the processor chain
            method_name(str): Name of the method called on the logger to log the message
            event_dict(dict): The event dict containing the log context

        Returns:
            dict: structlog event_dict with combined log fields added and renamed according to the elastic common schema.

        """
        try:
            if logger and logger.name == self.target_logger:
                original_event = event_dict['event']
                result = self._parse_log(original_event)
                request_fields = self._parse_request(result['request'])
                result.update(request_fields)

                user_agent_fields = self._parse_user_agent(result['agent'])
                message = '"{0}" {1} {2}'.format(result['request'], result['status'], result['size'])
                ecs_fields = self._convert_to_ecs(result)
                ecs_fields.update(user_agent_fields)
                ecs_fields['message'] = message
                ecs_fields['event.original'] = original_event
                event_dict.update(ecs_fields)
        finally:
            return event_dict

    def _parse_log(self, message):
        parts = [
            r'(?P<host>\S+)',  # host %h
            r'\S+',  # indent %l (unused)
            r'(?P<user>\S+)',  # user %u
            r'\[(?P<time>.+)\]',  # time %t
            r'"(?P<request>.+)"',  # request "%r"
            r'(?P<status>[0-9]+)',  # status %>s
            r'(?P<size>\S+)',  # size %b (careful, can be '-')
            r'"(?P<referrer>.*)"',  # referrer "%{Referrer}i"
            r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
        ]
        pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')
        match = pattern.match(message)
        if match:
            result = match.groupdict()
            if result["user"] == "-":
                result["user"] = None
            result["status"] = int(result["status"])
            if result["size"] == "-":
                result["size"] = 0
            else:
                result["size"] = int(result["size"])
            if result["referrer"] == "-":
                result["referrer"] = None
            return result
        else:
            return dict()

    def _parse_request(self, request):
        request_matcher = r'(?P<method>\S+)\s+(?P<url>\S+)\s+HTTP/(?P<version>\S+)'
        pattern = re.compile(request_matcher)
        match = pattern.match(request)
        if match:
            result = match.groupdict()
            if 'method' in result:
                result['method'] = result['method'].lower()
            return result
        else:
            return dict()

    def _parse_user_agent(self, agent_string):
        user_agent = parse(agent_string)
        result = dict()
        result['user_agent.original'] = agent_string
        result['user_agent.name'] = user_agent.browser.family
        result['user_agent.os.name'] = user_agent.os.family
        result['user_agent.os.version'] = user_agent.os.version_string
        result['user_agent.os.full'] = ' '.join([user_agent.os.family,user_agent.os.version_string])
        result['user_agent.device.name'] = user_agent.device.family
        result['user_agent.version'] = user_agent.browser.version_string
        return result

    def _convert_to_ecs(self,parsed_fields):
        result = dict()
        parsed_fields.pop('request',None)
        parsed_fields.pop('agent',None)
        for key, value in parsed_fields.items():
            result[_ecs_field_mappings[key]]=value
        return result







