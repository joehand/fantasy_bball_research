# -*- coding: utf-8 -*-
"""
    fantasy.players.models
    ~~~~~~~~~

    player models.

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

from ..extensions import db


class Team(db.Document):
    name = db.StringField(unique=True)


class Player(db.Document):
    """  All the players!
    """
    name = db.StringField(unique=True)
    team = db.ReferenceField(Team)
    pos = db.StringField()
    stats = db.DictField()
    proj = db.DictField()
    zscores = db.DictField()
    drafted = db.BooleanField(default=False)
    rank = db.IntField()
    ranks = db.DictField()

    meta = {
        'ordering': ['rank']
    }
