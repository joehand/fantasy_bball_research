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
    name = db.StringField()


class Player(db.Document):
    """  All the players!
    """
    name = db.StringField()
    team = db.ReferenceField(Team)
    pos = db.StringField()
    stats = db.DictField()
    proj = db.DictField()
    drafted = db.BooleanField(default=False)
