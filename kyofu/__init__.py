from logging import getLogger
from logging.config import dictConfig

from kyofu.config import logger_config
from kyofu.setup import setup_database_connection
from kyofu.model import sqla_metadata

dictConfig(logger_config)

logger = getLogger(__name__)
engine, session = setup_database_connection()
sqla_metadata.bind = engine
