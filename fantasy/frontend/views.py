# -*- coding: utf-8 -*-
"""
    fantasy.frontend.views
    ~~~~~~~~~

    Frontend views

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""
import os
import re
from collections import OrderedDict

from flask import (Blueprint, current_app, flash, g, jsonify,
                    redirect, render_template, request, url_for)

from flask_classy import FlaskView, route

import numpy as np
from pandas import Series, DataFrame

from .plot import create_plot, SAVE_DIR
from ..players import Player, LeagueStats

frontend = Blueprint('frontend', __name__, url_prefix='')

NUM_TEAMS = 12
STAT_CATS = ['PTS', 'REB', 'BLK','STL', 'AST', '3PM']
POS = ['PG', 'SG', 'SF', 'PF', 'C']
DRAFT_POS = ['PG', 'SG', 'SF', 'PF', 'C', 'F/C', 'G', 'UTIL', 'BENCH']

class Frontend(FlaskView):
    """ Frontend View Class
    """

    route_base = '/'

    @route('/', endpoint='index')
    def index(self):
        """ Index page
        """
        players = Player.objects()
        stats = LeagueStats.objects().first()

        drafted = players.filter(drafted=True)
        undrafted = players.filter(drafted=False, rank__lte=120)

        undrafted_pos = OrderedDict()
        undrafted_per = OrderedDict()
        for pos in POS:
            undrafted_pos[pos] = undrafted.filter(pos=pos)
            undrafted_per[pos] = 100 * (len(undrafted_pos[pos])/len(undrafted))

        drafted_remain = OrderedDict()
        drafted_per = OrderedDict()
        for draft_pos in DRAFT_POS:
            num_players = NUM_TEAMS
            pos_players = drafted.filter(draft_pos=draft_pos)
            if draft_pos == 'BENCH':
                num_players = NUM_TEAMS * 2
                print(num_players)
            drafted_remain[draft_pos] = num_players - len(pos_players)
            drafted_per[draft_pos] = 100 * (drafted_remain[draft_pos]/num_players)


        bigs = [play for play in undrafted if play.pos in ['PF', 'C']]
        bigs_big = [play for play in undrafted.order_by('rank_big') if play.pos in ['PF', 'C']]

        zscores_per = OrderedDict()
        for stat in STAT_CATS:
            zscores_per[stat] = 100 * (np.sum([play.adj_zscores[stat] for play in undrafted])/
                                np.sum([play.adj_zscores[stat] for play in players[:120]]))

        data = {
            'undraft': undrafted,
            'undraft_bigs' : bigs,
            'undraft_bigs_big' : bigs_big,
            'undraft_pos': undrafted_pos,
            'undraft_per': undrafted_per,
            'percent': undrafted_per,
            'draft_rem': drafted_remain,
            'draft_per': drafted_per,
            'zscores_per' : zscores_per,
        }
        return render_template('frontend/index.html',
                players=players, data=data, stats=stats)

    @route('/plot/', endpoint='plot')
    @route('/plot/<name>/', endpoint='plot')
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

        plot_file2 = 'undrafted_' + name + '.html'
        if (request.args.get('update') or not
                        os.path.exists(os.path.join(SAVE_DIR, plot_file2))):
            players = Player.objects()
            plot_file2 = create_plot(players, plot='undrafted_' + name)

        return render_template('frontend/plot.html', plot_file=plot_file)

    @route('/player_form/', endpoint='form', methods=['POST'])
    def player_form(self):
        print (request.form)
        name = request.form['player-name']
        print(name)
        return redirect(url_for('players.player', name=name))

    @route('/player_names/')
    def player_names(self):
        players = Player.objects()
        return jsonify(items=[player.name for player in players])

Frontend.register(frontend)
