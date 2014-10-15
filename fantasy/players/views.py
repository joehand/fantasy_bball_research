# -*- coding: utf-8 -*-
"""
    fantasy.players.views
    ~~~~~~~~~

    Frontend views

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""
import io

from flask import (Blueprint, current_app, flash, g, jsonify,
                    redirect, render_template, request, url_for)

from flask_classy import FlaskView, route

import requests
import pandas as pd

from .models import Player, Team

DRAFT_SHEET_URL = 'https://docs.google.com/spreadsheet/ccc?key=19YpHBaqzp4uccm1q7BgT3ssC_U_TtPaP705xUsHIxN0&gid=1178982124&output=csv'

players = Blueprint('players', __name__, url_prefix='/players')

def update_draft_data(player):
    name = player['PLAYER']
    player_db = Player.objects(name=name).first()

    if player_db is None:
        flash('Error updating player: {}'.format(name))
    else:
        player_db.drafted = player['DRAFTED']
        player_db.price = player['PRICE']
        player_db.keep = player['KEEPER']
        player_db.owner = player['OWNER']
        player_db.draft_pos = player['DRAFT_POS']
        player_db.save()
    return player

class Players(FlaskView):
    """ Frontend View Class
    """

    route_base = '/'

    @route('/', endpoint='index')
    def index(self):
        """ Index page
        """
        players = Player.objects()
        if request.args.get('undrafted'):
            players = players.filter(drafted=False)
        return render_template('players/index.html', players=players)


    @route('/draft/', endpoint='draft')
    def draft(self):
        """ Add updated draft info to players DB
        """
        if request.args.get('update'):
            response = requests.get(DRAFT_SHEET_URL)
            assert response.status_code == 200, 'Wrong status code'

            df = pd.read_csv(io.BytesIO(response.content))
            df['PRICE'] = df['PRICE'].apply(lambda x: x.replace('$','')).astype(int)
            df['DRAFTED'] = True
            df.apply(update_draft_data, axis=1)

            flash('Player Data Updated for draft')
        players = Player.objects(drafted=True)
        return render_template('players/draft.html', players=players)



    @route('/<name>/', endpoint='player')
    def player(self, name=None):
        """
        """
        player = Player.objects(name=name).first_or_404()
        return render_template('players/player.html', player=player)



Players.register(players)
