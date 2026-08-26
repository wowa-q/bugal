import logging

from .giro_parser import GiroDKBCSVParser
from .visa_parser import VisaDKBCSVParser
from .generic import GenericCSVParser

logger = logging.getLogger(__name__)

PARSERS = [GiroDKBCSVParser, VisaDKBCSVParser, GenericCSVParser]


def get_parser(filepath: str):
    logger.info(f'ParserRegistry.get_parser: Searching for parser for {filepath}')
    for parser_class in PARSERS:
        parser = parser_class()
        logger.info(f'ParserRegistry.get_parser: Testing {parser_class.__name__}')
        if parser.detect(filepath):
            logger.info(f'ParserRegistry.get_parser: Matched {parser_class.__name__}')
            return parser
    logger.warning(f'ParserRegistry.get_parser: No parser found (should not happen)')
    return None
