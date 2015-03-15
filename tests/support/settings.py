from datetime import timedelta
DEBUG = False
TESTING = True

LOGFILE="/tmp/segue-testing.log"

SQLALCHEMY_POOL_SIZE = None
SQLALCHEMY_POOL_TIMEOUT = None
SQLALCHEMY_POOL_RECYCLE = None
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

LOGFILE = '/var/log/segue/segue.log'

FRONTEND_URL = 'http://localhost:9000'
BACKEND_URL = 'http://192.168.33.91:9001'

JWT_SECRET_KEY = 'sshh'
JWT_DEFAULT_REALM = 'Login Required'
JWT_AUTH_URL_RULE = None
JWT_AUTH_ENDPOINT = None
JWT_ALGORITHM     = 'HS256'
JWT_VERIFY        = True
JWT_LEEWAY        = 0
JWT_VERIFY_EXPIRATION =  True
JWT_EXPIRATION_DELTA = timedelta(days=30)

CORS_HEADERS = 'Content-Type,Authorization'
CORS_ORIGINS = '*'
