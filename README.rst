==========================================================================
``structlog-extensions-nralbers``:  Extension processors for ``structlog``
==========================================================================

.. -begin-short-

Structlog extensions are a set of `structlog <http://www.structlog.org/en/stable/>`_ processors and utility functions
to add new logging options to structlog. The primary purpose is to supply tools to convert existing structlog
logging output into `Elastic Common Schema <https://www.elastic.co/guide/en/ecs/current/index.html>`_
json output so users can easily plug their application output into centralised logging solutions such as
`ELK stack <https://www.elastic.co/what-is/elk-stack>`_.

At present the extensions consist of a ``CombinedLogParser`` (which for example can be used to convert gunicorn access log
output into ECS fields), and the ``NestedDictJSONRenderer``, which can be used to convert the output of the CombinedLogParser
into ECS json format output.

.. -end-short-

Usage
=====

.. -begin-usage-

``CombinedLogParser``
---------------------

This processor will parse events formatted in Apache Combined log format into
Elastic common schema fields.

Example
^^^^^^^

This is an example for configuring gunicorn to emit json logs.

``gunicorn.conf.py``

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
--------------------------

This processor will convert key names using a specified separator into nested dictionaries prior to rendering the
output as JSON using the structlog JSONRenderer. This processor can for example convert Elastic Common Schema namespaced
keynames produced by the ``CombinedLogParser`` into the nested JSON format that ECS specifies. This processor must be the
final processor in a chain because it renders the output as a string instead of passing along an event dictionary.

Example
^^^^^^^

When using this logging initialisation:

        .. code-block:: python

            # --- std logging initialisation code using structlog rendering
            import structlog
            import structlog_extensions

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

.. --end-usage-