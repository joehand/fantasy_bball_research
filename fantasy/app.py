# -*- coding: utf-8 -*-
"""
    fantasy.app
    ~~~~~~~~~

    This module creates the fantasy application and configures extensions/blueprints

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

import os

from flask import Flask, render_template, send_from_directory

from .frontend import frontend
from .players import players

from .config import Config, DevelopmentConfig, ProductionConfig
from .extensions import assets, db

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    frontend,
    players,
)

def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = Config.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_favicon(app)

    return app

def configure_app(app, config=None):
    """ Allow for various configurations
        Default is Local (if available) or Development

        Local config to keep track non-public things (pw, api details, etc.)
        These will be stored in env variables for production

        See config.py for more details
    """
    # http://flask.pocoo.org/docs/api/#configuration
    if config:
        app.config.from_object(config)
    else:
        try:
            from .local import LocalConfig
            app.config.from_object(LocalConfig)
        except:
            app.config.from_object(DevelopmentConfig)

def configure_extensions(app):
    # flask-assets
    assets.init_app(app)

    # flask-mongoengine
    db.init_app(app)

def configure_blueprints(app, blueprints):
    """ Configure blueprints from list above or arg."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_template_filters(app):
    """ Add template filters here.
        These functions will be available in the jinja template.
    """

    @app.template_filter()
    def format_date(value, format='%d %b %Y'):
        return value.strftime(format)


def configure_logging(app):
    """ Configure logging for testing or production emails

        Not being used right now. TODO: this.
    """

    if app.debug or app.testing:
        #skip loggin
        return

def configure_hook(app):
    """ Applicaiton wide hooks (before, after requests)
    """

    @app.before_request
    def before_request():
        pass

def configure_error_handlers(app):
    """ Error pages, just in case =)
    """

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template('errors/500.html'), 500

def configure_favicon(app):

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
