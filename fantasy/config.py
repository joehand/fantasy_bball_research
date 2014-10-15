# -*- coding: utf-8 -*-
"""
    fantasy.config
    ~~~~~~~~~

    Config file for fantasy app (dev and production)

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    PROJECT = 'fantasy'

    # Get project and app root path
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))

    DEBUG = True
    PRODUCTION = False

    SECRET_KEY = 'this_is_so_secret' #used for development, reset in prod

    # Flask Assets Config
    ASSETS_MANIFEST = 'file:%s' % 'webcache'

class ProductionConfig(Config):

    DEBUG = False
    PRODUCTION = True

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Flask Security Config
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    # Flask Assets Config
    ASSETS_AUTO_BUILD = False
    FLASK_ASSETS_USE_S3 = True


class DevelopmentConfig(Config):

    DEBUG = True

    # MongoDB Config
    MONGODB_SETTINGS = {
        'db': 'fantasy_ball_db',
        'host':'localhost',
        'port':27017,
        'tz_aware':True
    }
