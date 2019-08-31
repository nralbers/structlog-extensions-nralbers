import re
from user_agents import parse

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

def convert_combined_log_to_ecs(log_line):
    result = _parse_log_into_fields(log_line)
    request_fields = _parse_request_section(result['request'])
    result.update(request_fields)
    user_agent_fields = _parse_user_agent_section(result['agent'])
    message = '"{0}" {1} {2}'.format(result['request'], result['status'], result['size'])
    ecs_fields = _convert_field_names_to_ecs(result)
    ecs_fields.update(user_agent_fields)
    ecs_fields['message'] = message
    ecs_fields['event.original'] = log_line
    return ecs_fields

def _parse_log_into_fields(log_line):
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
    match = pattern.match(log_line)
    if match:
        fields = match.groupdict()
        if fields["user"] == "-":
            fields["user"] = None
        fields["status"] = int(fields["status"])
        if fields["size"] == "-":
            fields["size"] = 0
        else:
            fields["size"] = int(fields["size"])
        if fields["referrer"] == "-":
            fields["referrer"] = None
        return fields
    else:
        return dict()

def _parse_request_section(request_string):
    request_matcher = r'(?P<method>\S+)\s+(?P<url>\S+)\s+HTTP/(?P<version>\S+)'
    pattern = re.compile(request_matcher)
    match = pattern.match(request_string)
    if match:
        request_fields = match.groupdict()
        if 'method' in request_fields:
            request_fields['method'] = request_fields['method'].lower()
        return request_fields
    else:
        return dict()

def _parse_user_agent_section(agent_string):
    user_agent = parse(agent_string)
    result = dict()
    result['user_agent.original'] = agent_string
    result['user_agent.name'] = user_agent.browser.family
    result['user_agent.os.name'] = user_agent.os.family
    result['user_agent.os.version'] = user_agent.os.version_string
    result['user_agent.os.full'] = ' '.join([user_agent.os.family, user_agent.os.version_string])
    result['user_agent.device.name'] = user_agent.device.family
    result['user_agent.version'] = user_agent.browser.version_string
    return result

def _convert_field_names_to_ecs(parsed_fields):
    ecs_fields = {_ecs_field_mappings[key]:value for (key,value) in parsed_fields.items() if key in _ecs_field_mappings}
    return ecs_fields