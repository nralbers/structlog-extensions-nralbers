from .utils import convert_combined_log_to_ecs
"""
structlog_extensions.processors 

This module contains processors for structlog.
"""

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
                ecs_fields = convert_combined_log_to_ecs(original_event)
                event_dict.update(ecs_fields)
        finally:
            return event_dict









