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

NUM_TEAMS = 12
PLAYERS_PER_TEAM = 10
BENCH_PLAYERS = 2
TOTAL_DOLLARS = 200 * NUM_TEAMS
TOTAL_PLAYERS = PLAYERS_PER_TEAM * NUM_TEAMS

STAT_CATS = ['PTS', 'REB', 'BLK', 'AST', 'STL', '3PM']

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
    min_zscores = db.DictField()
    dollars_spent = db.IntField()
    dollars_tot_zscore = db.FloatField()
    dollars_big_zscore = db.FloatField()
    proj_dollars_tot_zscore = db.FloatField()
    proj_dollars_big_zscore = db.FloatField()
    live_dollars_tot_zscore = db.FloatField()
    live_dollars_big_zscore = db.FloatField()


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
    adj_zscores = db.DictField()

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
            self.calc_player_totals()

        self.update_draft_values()

        min_tot_zscore = self.league_stats['min_total_zscore']
        min_big_zscore = self.league_stats['min_big_zscore']

        self.adj_tot_zscore = self.tot_zscore + abs(min_tot_zscore)
        self.adj_big_zscore = self.big_zscore + abs(min_big_zscore)

        for cat in STAT_CATS:
            cat_min_zscore = self.league_stats['min_zscores'][cat]
            self.adj_zscores[cat] = (self.zscores['AVG'][cat + '_AVG_Zscore']
                                        + abs(cat_min_zscore))

    def set_rank_big(self):
        return self.ranks['RANK_BIG']

    @property
    def has_stats(self):
        if not self.stats or np.isnan(self.sorted_stats[0][1]):
            if self.stats:
                self.stats = None
                self.save()
            return False
        return True

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
        if self.stats:
            stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
            stats = {key.split('_')[0]:val for key, val in self.stats.items()}
            return list((i, stats.get(i)) for i in stat_order)
        return None

    @property
    def sorted_proj(self):
        stat_order = ['MIN', 'PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.proj['AVG'].items()}
        return list((i, stats.get(i)) for i in stat_order)

    @property
    def sorted_zscores(self):
        stat_order = ['PTS', 'REB', 'BLK', 'STL', 'AST', '3PM']
        stats = {key.split('_')[0]:val for key, val in self.zscores['AVG'].items()}
        return list((i, stats.get(i)) for i in stat_order)

    @property
    def proj_cost_tot(self):
        # give all bench players $1
        if self.rank >= (TOTAL_PLAYERS - BENCH_PLAYERS):
            cost = 1
            return cost
        cost = int(self.league_stats['dollars_tot_zscore'] * self.adj_tot_zscore)
        return cost

    @property
    def proj_cost_big(self):
        # give all bench players $1
        if self.rank_big >= (TOTAL_PLAYERS - BENCH_PLAYERS):
            cost = 1
            return cost
        cost =  int(self.league_stats['dollars_big_zscore'] * self.adj_big_zscore)
        return cost

    @property
    def live_cost_tot(self):
        cost = int(self.league_stats['live_dollars_tot_zscore'] * self.adj_tot_zscore)
        if cost < 1:
            cost = 1
        return cost

    @property
    def live_cost_big(self):
        cost =  int(self.league_stats['live_dollars_big_zscore'] * self.adj_big_zscore)
        if cost < 1:
            cost = 1
        return cost


    @classmethod
    def update_draft_values(cls):
        print('updating draft values for player class')
        drafted = cls.objects(drafted=True)
        dollars_spent = np.sum([play.price for play in drafted])
        dollars_tot_zscore = np.mean([play.dollar_tot_zscore for play in drafted])
        dollars_big_zscore = np.mean([play.dollar_big_zscore for play in drafted])

        stats = LeagueStats.objects().first()
        stats.dollars_spent = dollars_spent
        stats.dollars_tot_zscore = dollars_tot_zscore
        stats.dollars_big_zscore = dollars_big_zscore

        # update dollar values
        # assume bench players sell at $1 each
        dollars_left = TOTAL_DOLLARS - dollars_spent
        undrafted_players = cls.objects(drafted=False, rank__lte=120)

        live_dollars_tot_zscore = dollars_left/np.sum(
                [play.adj_tot_zscore for play in undrafted_players])

        live_dollars_big_zscore = dollars_left/np.sum(
                [play.adj_big_zscore for play in undrafted_players])

        stats.live_dollars_tot_zscore = live_dollars_tot_zscore
        stats.live_dollars_big_zscore = live_dollars_big_zscore

        stats.save()
        return stats

    @classmethod
    def calc_player_totals(cls):
        players = cls.objects()
        stats = LeagueStats.objects().first()

        lowest = players.order_by('-rank').first()
        min_total_zscore = lowest.tot_zscore

        lowest_big = players.order_by('-rank_big').first()
        min_big_zscore = lowest_big.big_zscore

        stats.min_total_zscore = min_total_zscore
        stats.min_big_zscore = min_big_zscore

        for cat in STAT_CATS:
            min_cat_zscore = np.min([play.zscores['AVG'][cat + '_AVG_Zscore']
                                        for play in players])
            stats.min_zscores[cat] = min_cat_zscore

        # assume bench players sell at $1 each
        dollars_starting_players = TOTAL_DOLLARS - (BENCH_PLAYERS * NUM_TEAMS * 1)
        non_bench_players = players[:(TOTAL_PLAYERS - BENCH_PLAYERS)]

        proj_dollars_tot_zscore = dollars_starting_players/np.sum(
                [play.adj_tot_zscore for play in non_bench_players])

        proj_dollars_big_zscore = dollars_starting_players/np.sum(
                [play.adj_big_zscore for play in non_bench_players])

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
        for key in ['proj_cost_tot', 'proj_cost_big', 'live_cost_tot', 'live_cost_big']:
            data[key] = getattr(self,key)
        for key, val in list(data.items()):
            if key == 'team':
                data[key] = str(self[key].name)
            elif key == '_id':
                data[key] = str(self.id)
        data = flatten_dict(data)
        return data
