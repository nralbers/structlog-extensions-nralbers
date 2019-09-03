==========================================================================
``structlog-extensions-nralbers``:  Extension processors for ``structlog``
==========================================================================



``CombinedLogParser``
=====================

This processor will parse events formatted in Apache Combined log format into
Elastic common schema fields.

Usage
-----
This is an example for configuring gunicorn to emit json logs.

.. code-block:: python

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


``NestedDictJSONRenderer``
=================================================

This processor will convert key names using a specified separator into nested dictionaries prior to rendering the
output as JSON using the structlog JSONRenderer. This processor can for example convert Elastic Common Schema namespaced
keynames produced by the ``CombinedLogParser`` into the nested JSON format that ECS specifies. This processor must be the
final processor in a chain because it renders the output as a string instead of passing along an event dictionary.

Example
-------
An event dictionary with the following key/value pairs
:code:`{ 'http.request.method': 'get', 'http:.request.referrer': 'http://www.example.com', 'http.version': '1.0'}`

will render into json as:

.. code-block:: python

    { 'http': { 'version': '1.0',
                'request': { 'method': 'get',
                             'referrer': 'http://www.example.com'}
                }
    }
