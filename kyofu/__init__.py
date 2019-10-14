from kyofu.config import logger_config
from logging.config import dictConfig
from logging import getLogger

dictConfig(logger_config)

logger = getLogger(__name__)
