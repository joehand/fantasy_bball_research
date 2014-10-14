# -*- coding: utf-8 -*-
"""
    fantasy.extensions
    ~~~~~~~~~

    Extensions file for fantasy app

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""
from flask_assets import Environment
assets = Environment()

from flask_mongoengine import MongoEngine
db = MongoEngine()
