# -*- coding: utf-8 -*-
"""
    fantasy.frontend.views
    ~~~~~~~~~

    Frontend views

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""
import os

from flask import (Blueprint, current_app, flash, g, jsonify,
                    redirect, render_template, request, url_for)

from flask_classy import FlaskView, route

from .plot import create_plot, SAVE_DIR
from ..players import Player

frontend = Blueprint('frontend', __name__, url_prefix='')


class Frontend(FlaskView):
    """ Frontend View Class
    """

    route_base = '/'

    @route('/', endpoint='index')
    def index(self):
        """ Index page
        """
        players = Player.objects()
        undrafted =players.filter(drafted=False, rank__lte=120)
        pg =  undrafted.filter(pos='PG')
        sg = undrafted.filter(pos='SG')
        sf = undrafted.filter(pos='SF')
        pf = undrafted.filter(pos='PF')
        c = undrafted.filter(pos='C')
        data = {
            'undraft': undrafted,
            'pg_undraft':pg,
            'sg_undraft':sg,
            'sf_undraft':sf,
            'pf_undraft':pf,
            'c_undraft':c,
            'percent' : {
                'pg': 100 * (len(pg)/len(undrafted)),
                'sg': 100 * (len(sg)/len(undrafted)),
                'sf': 100 * (len(sf)/len(undrafted)),
                'pf': 100 * (len(pf)/len(undrafted)),
                'c': 100 * (len(c)/len(undrafted)),
            }
        }
        return render_template('frontend/index.html', data=data)

    @route('/plot/', endpoint='plot')
    @route('/plot/<name>', endpoint='plot')
    def plot(self, name=None):
        """ Index page
        """
        if name is None:
            name = 'all'
        plot_file = name + '.html'

        if (request.args.get('update') or not
                os.path.exists(os.path.join(SAVE_DIR, plot_file))):
            players = Player.objects()
            plot_file = create_plot(players, plot=name)
        return render_template('frontend/plot.html', plot_file=plot_file)

Frontend.register(frontend)
