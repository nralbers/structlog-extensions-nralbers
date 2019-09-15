import structlog
import structlog_extensions

# --- Structlog logging initialisation code

pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog_extensions.processors.CombinedLogParser("gunicorn.access")
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

accesslog = '-'
errorlog = '-'
bind = '0.0.0.0:5000'