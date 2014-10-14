# -*- coding: utf-8 -*-
"""
    fantasy.players.views
    ~~~~~~~~~

    Frontend views

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

from flask import (Blueprint, current_app, flash, g, jsonify,
                    redirect, render_template, request, url_for)

from flask_classy import FlaskView, route


players = Blueprint('players', __name__, url_prefix='/players')

class Players(FlaskView):
    """ Frontend View Class
    """

    route_base = '/'

    @route('/', endpoint='index')
    def index(self):
        """ Index page
        """
        return render_template('frontend/index.html')

Players.register(players)
