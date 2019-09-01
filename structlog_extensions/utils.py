import re
from user_agents import parse
from deepmerge import  always_merger
import pytz
from datetime import datetime, timezone


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


def convert_combined_log_to_ecs(log_line, dataset, severity=0):
    """
    Converts a combined log entry into a dict containing the log entry key/values
    with the key names using Elastic Common schema element names.

    Args:
        log_line (str): Combined log entry
        dataset (str): source of the log entry (for example 'apache.access')
        severity (int, optional): severity of the source log event

    Returns:
        dict: Dictionary of key/value pairs with the key names using ECS namespaced names.
    """
    result = _parse_log_into_fields(log_line)
    request_fields = _parse_request_section(result['request'])
    result.update(request_fields)
    user_agent_fields = _parse_user_agent_section(result['agent'])
    message = '"{0}" {1} {2}'.format(result['request'], result['status'], result['size'])
    ecs_fields = _convert_field_names_to_ecs(result)
    ecs_fields.update(user_agent_fields)
    ecs_fields['message'] = message
    ecs_fields['event.original'] = log_line
    ecs_fields['event.dataset'] = dataset
    ecs_fields['ecs.version'] = '1.0.0'
    ecs_fields['event.created'] = datetime.now(timezone.utc).isoformat()
    ecs_fields['@timestamp'] = combined_log_timestring_to_iso(ecs_fields['@timestamp'])
    ecs_fields['event.severity'] = severity
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
    ecs_fields['event.action'] = ecs_fields['http.request.method']
    return ecs_fields

def unflatten_dict(flat_dict, separator='.'):
    """
    Turns a dict with key names defining a namespace into a nested dictionary

    Args:
        flat_dict (dict): The dict cont
        separator (str, optional): The separator used to split name elements. Default '.'

    Returns:
        dict: A nested dictionary structure created from the original flat dict.
    """
    expanded_dict = dict()
    for key, value in flat_dict.items():
        field_hierarchy = key.split(separator)
        for field in reversed(field_hierarchy):
            item = { field: value}
            value = item
        always_merger.merge(expanded_dict,value)
    return expanded_dict


def _parse_datetime(timestamp):
    '''
    Parses datetime with timezone formatted as:
        `day/month/year:hour:minute:second zone`

    Example:
        `>>> parse_datetime('13/Nov/2015:11:45:42 +0000')`
        `datetime.datetime(2015, 11, 3, 11, 45, 4, tzinfo=<UTC>)`

    Due to problems parsing the timezone (`%z`) with `datetime.strptime`, the
    timezone will be obtained using the `pytz` library.
    '''
    dt = datetime.strptime(timestamp[0:-6], '%d/%b/%Y:%H:%M:%S')
    dt_tz = int(timestamp[-5:-2]) * 60 + int(timestamp[-2:])
    return dt.replace(tzinfo=pytz.FixedOffset(dt_tz))


def combined_log_timestring_to_iso(timestamp):
    """
    converts a combined log format date/time entry into an iso standard datetime string
    Args:
        timestamp (str): Datetime log entry to convert

    Returns:
        str: iso standard datetime string
    """
    dt = _parse_datetime(timestamp)
    return dt.isoformat()

