import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MATCH_PER_PAGE = 3
    NEWS_PER_PAGE = 10
    REGISTRATION_OPEN = os.environ.get('REGISTRATION_OPEN') or False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND') is not None
    RENDER_EMAIL = os.environ.get('RENDER_EMAIL') is not None

    ADMINS = [('ICC4 darts','icc4darts@gmail.com'),('ICC4 darts errors','icc4darts+errors@gmail.com')]
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    UPLOADS_DEFAULT_DEST = os.environ.get('UPLOAD_FOLDER') or 'app/var/tmp/uploads'
    IMAGE_DEST = os.environ.get('IMAGE_FOLDER') or 'app/var/images'

    S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
    S3_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
    AWS_DEFAULT_REGION = os.environ.get('AWS_REGION')