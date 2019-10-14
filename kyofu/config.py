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
        'stderr': {
            'class': 'logging.StreamHandler',
            'level': 'WARN',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
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
            'handlers': ['stdout', 'stderr']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['null'],
    },
}
