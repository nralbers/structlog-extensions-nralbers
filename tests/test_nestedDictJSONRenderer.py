from unittest import TestCase
import logging
import structlog
import structlog_extensions
from structlog_extensions.processors import ConvertNamespacedKeysToNestedDictJSONRenderer

class TestNestedDictJSONRenderer(TestCase):
    def test_chain_processor(self):
        structlog.configure(
            processors=[
                structlog_extensions.processors.ConvertNamespacedKeysToNestedDictJSONRenderer(clean_keys=['event'], separator='_'),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        logger = structlog.get_logger(__name__)
        logger.warning('Test', event_original='Test', event_action='test', service_name='structlog_extensions', service_version='1.0.0' )

