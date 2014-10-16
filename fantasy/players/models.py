# -*- coding: utf-8 -*-
"""
    fantasy.players.models
    ~~~~~~~~~

    player models.

    :copyright: (c) 2014 by Joe Hand.
    :license:
"""

import json

import numpy as np

from ..extensions import db

TOTAL_DOLLARS = 200 * 12
TOTAL_PLAYERS = 10 * 12

def flatten_dict(root, prefix_keys=True):
    dicts = [([], root)]
    ret = {}
    seen = set()
    for path, d in dicts:
        if id(d) in seen:
            continue
        seen.add(id(d))
        for k, v in d.items():
            new_path = path + [k]
            prefix = '_'.join(new_path) if prefix_keys else k
            if hasattr(v, 'items'):
                dicts.append((new_path, v))
            else:
                ret[prefix] = v
    return ret

class Team(db.Document):
    name = db.StringField(unique=True)


class LeagueStats(db.Document):
    min_total_zscore = db.FloatField()
    min_big_zscore = db.FloatField()
    dollars_spent = db.IntField()
    dollars_tot_zscore = db.FloatField()
    dollars_big_zscore = db.FloatField()
    proj_dollars_tot_zscore = db.FloatField()
    proj_dollars_big_zscore = db.FloatField()


class Player(db.Document):
    """  All the players!
    """
    name = db.StringField(unique=True)
    league_stats = db.ReferenceField(LeagueStats)
    team = db.ReferenceField(Team)
    pos = db.StringField()
    stats = db.DictField()
    proj = db.DictField()
    zscores = db.DictField()
    drafted = db.BooleanField(default=False)
    rank = db.IntField()
    ranks = db.DictField()
    price = db.IntField()
    keep = db.BooleanField(default=False)
    owner = db.StringField()
    draft_pos = db.StringField()
    rank_big = db.IntField()
    adj_tot_zscore = db.FloatField()
    adj_big_zscore = db.FloatField()

    meta = {
        'ordering': ['rank']
    }

    def clean(self):
        if self.keep != True:
            self.keep = False

        if self.drafted != True:
            self.price = None

        self.rank_big = self.set_rank_big()

        if not self.league_stats:
            stats = LeagueStats.objects().first()
            if not stats:
                stats = LeagueStats()
                stats.save()
            self.league_stats = stats

        self.update_draft_values()
        self.calc_player_totals()

        min_tot_zscore = self.league_stats['min_total_zscore']
        min_big_zscore = self.league_stats['min_big_zscore']

        self.adj_tot_zscore = self.tot_zscore + abs(min_tot_zscore)
        self.adj_big_zscore = self.big_zscore + abs(min_big_zscore)

    def set_rank_big(self):
        return self.ranks['RANK_BIG']

    @property
    def tot_zscore(self):
        return self.zscores['AVG']['TOT_AVG_Zscore']

    @property
    def big_zscore(self):
        return self.zscores['AVG']['BIG_AVG_Zscore']

    @property
    def diff_zscore(self):
        return self.zscores['AVG']['DIFF_AVG_Zscore']

    @property
    def dollar_tot_zscore(self):
        if self.drafted:
            return float(self.price)/self.adj_tot_zscore
        return None

    @property
    def dollar_big_zscore(self):
        if self.drafted:
            return float(self.price)/self.adj_big_zscore
        return None

    @property
    def sorted_stats(self):
        stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.stats.items()}
        return list((i, stats.get(i)) for i in stat_order)

    @property
    def sorted_proj(self):
        stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.proj['AVG'].items()}
        return list((i, stats.get(i)) for i in stat_order)

    @property
    def proj_cost_tot(self):
        cost = int(self.league_stats['dollars_tot_zscore'] * self.adj_tot_zscore)
        if cost < 1:
            cost = 1
        return cost
        
    @property
    def proj_cost_big(self):
        cost =  int(self.league_stats['dollars_big_zscore'] * self.adj_big_zscore)
        if cost < 1:
            cost = 1
        return cost

    @classmethod
    def update_draft_values(cls):
        drafted = cls.objects(drafted=True)
        dollars_spent = np.sum([play.price for play in drafted])
        dollars_tot_zscore = np.mean([play.dollar_tot_zscore for play in drafted])
        dollars_big_zscore = np.mean([play.dollar_big_zscore for play in drafted])

        stats = LeagueStats.objects().first()
        stats.dollars_spent = dollars_spent
        stats.dollars_tot_zscore = dollars_tot_zscore
        stats.dollars_big_zscore = dollars_big_zscore
        stats.save()
        return stats

    @classmethod
    def calc_player_totals(cls):
        players = cls.objects()

        lowest = players.order_by('-rank').first()
        min_total_zscore = lowest.tot_zscore

        lowest_big = players.order_by('-rank_big').first()
        min_big_zscore = lowest_big.big_zscore

        proj_dollars_tot_zscore = TOTAL_DOLLARS/np.sum(
                [play.adj_tot_zscore for play in players[:TOTAL_PLAYERS]])

        proj_dollars_big_zscore = TOTAL_DOLLARS/np.sum(
                [play.adj_big_zscore for play in players[:TOTAL_PLAYERS]])

        stats = LeagueStats.objects().first()
        stats.min_total_zscore = min_total_zscore
        stats.min_big_zscore = min_big_zscore
        stats.proj_dollars_tot_zscore = proj_dollars_tot_zscore
        stats.proj_dollars_big_zscore = proj_dollars_big_zscore
        stats.save()
        return stats

    def flatten(self):
        """ MongoDB Object to JSON Object
            Returns flat JSON of model
        """
        data = json.loads(self.to_json())
        data.pop('_cls', None)
        for key in ['proj_cost_tot', 'proj_cost_big']:
            data[key] = getattr(self,key)
        for key, val in list(data.items()):
            if key == 'team':
                data[key] = str(self[key].name)
            elif key == '_id':
                data[key] = str(self.id)
        data = flatten_dict(data)
        return data
