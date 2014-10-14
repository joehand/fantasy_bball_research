# -*- coding: utf-8 -*-
"""
    fantasy.frontend.views
    ~~~~~~~~~

    Frontend views

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

from flask import (Blueprint, current_app, flash, g, jsonify,
                    redirect, render_template, request, url_for)

from flask_classy import FlaskView, route


frontend = Blueprint('frontend', __name__, url_prefix='')

class Frontend(FlaskView):
    """ Frontend View Class
    """

    route_base = '/'

    @route('/', endpoint='index')
    def index(self):
        """ Index page
        """
        return render_template('frontend/index.html')

    @route('/', endpoint='chart')
    def chart(self):
        """ Index page
        """
        return render_template('frontend/index.html')

Frontend.register(frontend)
