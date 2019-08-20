import re
"""
structlog_extensions.processors 

This module contains processors for structlog.
"""

class CombinedLogParser:
    """
    Parses Apache combined log style entries in the event field into separate fields

    Attributes:
        loggerfilter: field used to identify which logger is emitting combined log messages
    """
    def __init__(self, loggerfilter):
        self.loggerfilter = loggerfilter

    def parse_combined_log(self, logger, method_name, event_dict):
        """
        Filter function to parse combined logs.

        Add to the structlog processors list or the stdlib logger
        foreign_pre_chain list to apply splitting of combined log entries to log entries.

        Args:
            logger(object): Logger object passed by the processor chain
            method_name(str): Name of the method called on the logger to log the message
            event_dict(dict): The event dict containing the log context

        Returns:
            dict: Modified event_dict

        """
        try:
            if logger and logger.name == self.loggerfilter:
                message = event_dict['event']
                res = self._parse_log(message)

                event_dict.update(res)
        finally:
            pass

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
            r'"(?P<referer>.*)"',  # referer "%{Referer}i"
            r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
        ]
        pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')
        m = pattern.match(message)
        res = m.groupdict()
        if res["user"] == "-":
            res["user"] = None
        res["status"] = int(res["status"])
        if res["size"] == "-":
            res["size"] = 0
        else:
            res["size"] = int(res["size"])
        if res["referer"] == "-":
            res["referer"] = None
        return res






