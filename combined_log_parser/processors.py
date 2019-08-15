import re


class CombinedLogParser:
    def __init__(self, loggerfilter):
        self.loggerfilter = loggerfilter

    def parse_combined_log(self, logger, method_name, event_dict):
        if event_dict.get('logger') == self.loggerfilter:
            message = event_dict['event']

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

            event_dict.update(res)

        return event_dict
