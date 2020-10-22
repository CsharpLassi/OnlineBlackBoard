import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SESSION_TYPE = 'filesystem'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'http'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, '..', '..', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BLACKBOARD_DATA_PATH = os.environ.get('SESSION_DATA_PATH') or 'blackboard_data'
