"""
structlog_extensions.processors

This module contains processors for structlog.
"""
import structlog
from .utils import convert_combined_log_to_ecs, unflatten_dict
import logging


class NestedDictJSONRenderer(structlog.processors.JSONRenderer):
    """
    Structlog processor for creating JSON output including nested key output. It assumes that any key name
    using the specified separator is actually multiple nested keys, and will transform the log event dictionary to
    reflect this. The primary use case is for turning
    'flat' key-value pairs into the sort of structured json seen in (for example) elastic common schema.

    Notes:
        Must be the last processor on a chain (when using structlog as a renderer),
        or the processor of a ``structlog.stdlib.ProcessorFormatter`` object when using logging as a renderer.

    Example:
        When using this logging initialisation:

        .. code-block:: python

            # --- std logging initialisation code using structlog rendering

            pre_chain = [
                # Add the log level and a timestamp to the event_dict if the log entry
                # is not from structlog.
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog_extensions.processors.CombinedLogParser("gunicorn.access")
            ]

            logging.dict_config( {
                        "version": 1,
                        "disable_existing_loggers": False,
                        "formatters": {
                            "json_formatter": {
                                "()": structlog.stdlib.ProcessorFormatter,
                                "processor": structlog_extensions.processors.NestedDictJSONRenderer('.'),
                                "foreign_pre_chain": pre_chain,
                            }
                        },
                        "handlers": {
                            "error_console": {
                                "class": "logging.StreamHandler",
                                "formatter": "json_formatter",
                            },
                            "console": {
                                "class": "logging.StreamHandler",
                                "formatter": "json_formatter",
                            }
                        },
                    })

        These entries (produced by ``structlog_extensions.processors.CombinedLogParser``):

        .. code-block:: python

            { 'http.request.method': 'get', 'http:.request.referrer': 'http://www.example.com', 'http.version': '1.0'}`

        will be transformed into the following nested json structure:

        .. code-block:: python

            { 'http': { 'version': '1.0',
                        'request': { 'method': 'get',
                                     'referrer': 'http://www.example.com'}
                        }
            }

    Notes:
        In cases where a root key has a value assigned and potential subkeys exist, the behaviour of this processor
        could be difficult to predict since it uses a deep merge that will perform overwriting in the order the keys
        are supplied by the event_dict. To prevent this happening, use the `clean_fields` attribute to specify the
        conflicting keys that should be removed from the event_dict prior to expansion.

    Attributes:
        separator (str, optional): Namespace separator. Default = '_'
        clean_keys (list, optional): List of keys to remove from log event prior to expansion. Intended for use when the original
                             log event has key names that might overlap with the root names of nested keys.
    """

    def __init__(self, *args, clean_keys=None, separator='_', **kwargs):
        self.clean_fields = clean_keys
        self.separator = separator
        super().__init__(*args, **kwargs)

    def __call__(self, logger, name, event_dict):
        if self.clean_fields:
            for field in self.clean_fields:
                event_dict.pop(field, None)
        try:
            nested_dict = unflatten_dict(event_dict, self.separator)
        finally:
            return super().__call__(logger,name,nested_dict)


class CombinedLogParser:
    """
    Parses Apache combined log style entries in the event field into separate fields using
    `Elastic Common Schema <https://www.elastic.co/guide/en/ecs/current/ecs-field-reference.html>`_ field names.

    Attributes:
        target_logger (str): Name of the logger object that is logging combined log output.

    Example:
        Creating and using a parser instance with structlog:

        .. code-block:: python

            import structlog_extensions
            import structlog
            import logging



            structlog.configure(
                processors=[
                    structlog_extensions.processors.CombinedLogParser('gunicorn.access'),
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

    def __call__(self, logger, method_name, event_dict):
        try:
            record = event_dict.get("_record")
            if record is None:
                logger_name = logger.name
            else:
                logger_name = record.name
            if logger_name == self.target_logger:
                if method_name in ['info', 'warn', 'warning', 'error', 'critical', 'debug']:
                    severity = getattr(logging, method_name.upper())
                else:
                    severity = 0
                original_event = event_dict['event']
                ecs_fields = convert_combined_log_to_ecs(log_line=original_event, dataset=logger_name,
                                                         severity=severity)
                event_dict.update(ecs_fields)
        finally:
            return event_dict



