import os

LOGFILE_SIZE = 10*1024*1024
LOGFILE_COUNT = 5
LOG_DIR = '/logs/'
LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(levelname)s %(asctime)s %(name)s  %(pathname)s %(funcName)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django_json.log'),
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'json',
        }
    },
    'loggers': {
        'sms_service': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    }
}


LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_TZ = False

AUTH_SERVICE_CHECK_TOKEN_URL = 'https://auth-service/check_token/'
AUTH_SERVICE_CHECK_PERM_URL = 'https://auth-service/check_perm/'
AUTH_TOKEN = '321'
SECRET_KEY = '123'
DEVINO_LOGIN = 'tester'
DEVINO_PASSWORD = '123'
