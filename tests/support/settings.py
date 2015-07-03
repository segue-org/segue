# -*- coding: utf-8 -*-

from datetime import timedelta
DEBUG = False
TESTING = True

LOGFILE="/tmp/segue-testing.log"

PRINTERS = []

SQLALCHEMY_POOL_SIZE = None
SQLALCHEMY_POOL_TIMEOUT = None
SQLALCHEMY_POOL_RECYCLE = None
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

LOGFILE = '/tmp/segue.log'
LOGLEVEL = 'DEBUG'

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

MAIL_SERVER = 'localhost'
MAIL_PORT   = 1025
MAIL_DEFAULT_SENDER = 'teste@softwarelivre.org'
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_USE_TLS = False
MAIL_BCC = 'test@example.com'

CORS_HEADERS = 'Content-Type,Authorization'
CORS_ORIGINS = '*'

PAGSEGURO_ENV='sandbox'

BOLETO_OFFSET        = 100000
BOLETO_TIPO_CONVENIO = 7
BOLETO_CARTEIRA      = "18"
BOLETO_AGENCIA       = "4422"
BOLETO_CONTA         = "22345"
BOLETO_CONVENIO      = "1600260"
BOLETO_CNPJ          = "01.222.682/0001-01"
BOLETO_ENDERECO      = "Rua Rufião Moura, 1234, cj 99 - Floresta - 90.920-008 - Porto Alegre/RS"
BOLETO_EMPRESA       = "Empresa Organizadora de Eventos Ltda"

STORAGE_DIR = '/tmp/'
