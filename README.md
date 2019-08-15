# structlog-combined-log-parser
Combined log parser processor class for use with structlog

If you have a logger that is passing apache combined log format strings in it's event field, you can use this processor 
in your processor chain to convert the event string into fields.

## Usage
This is an example for configuring gunicorn to emit json logs.

_gunicorn.conf.py_
```python
from combined_log_parser.processors import CombinedLogParser
import structlog

# --- Structlog logging initialisation code
timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
logparser = CombinedLogParser("gunicorn.access")
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    timestamper,
    logparser.parse_combined_log
]

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
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
}
```


