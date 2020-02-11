import os

DB_DRIVER = os.getenv('DB_DRIVER', 'mysql+pymysql')
DB_USER = os.getenv('DB_USER', 'kyofu')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'kyofu')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'kyofu')
DB_OPTION = os.getenv('DB_OPTION', 'charset=utf8mb4')

DB_URL = f'{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SCHEMA}' + f'?{DB_OPTION}' if DB_OPTION else ''
SQLALCHEMY_ENGINE_ECHO = os.getenv('SQLALCHEMY_ENGINE_ECHO ', False)

logger_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'null': {
            'class': 'logging.NullHandler',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'kyofu': {
            'level': 'DEBUG',
            'handlers': ['stdout'],
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['null'],
    },
}
