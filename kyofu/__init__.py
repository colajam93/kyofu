from logging import getLogger
from logging.config import dictConfig

from kyofu.config import logger_config
from kyofu.setup import setup_database_connection
from kyofu.model import sqla_metadata
from types import MethodType

dictConfig(logger_config)

logger = getLogger(__name__)
engine, session = setup_database_connection()

current_config = {
    'auto_commit': False,
}


def safe_commit(self, force: bool = False):
    from kyofu.util import show_proceed_prompt

    auto_commit = current_config.get('auto_commit', False)
    if auto_commit or force:
        self.kyofu_commit()
    else:
        if self.new or self.dirty or self.deleted:
            if show_proceed_prompt('Commit?'):
                self.kyofu_commit()
            else:
                self.rollback()


session.kyofu_commit = session.commit
session.commit = MethodType(safe_commit, session)
sqla_metadata.bind = engine
