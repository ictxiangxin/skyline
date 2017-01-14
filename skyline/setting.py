from residue.configure import GlobalConfigure
from residue.log import GlobalLog

configure = GlobalConfigure(
    {
        'log': {
            'path': 'skyline.log',
        },
        'dal': {
            'driver': {
                'driver_redis': {
                    'host': 'localhost',
                    'port': 6379,
                },
                'driver_file': {
                    'encoding': 'utf-8',
                }
            },
            'model': {
                'linear': {
                    'abstract': {
                        'file': {
                            'append': True,
                            'encoding': 'utf-8',
                        }
                    }
                }
            }
        }
    }
)

log = GlobalLog(configure.log.path)
