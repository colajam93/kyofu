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

