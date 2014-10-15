import pandas as pd

from fantasy.players import Team, Player

DATA_FILE = '../data/playerData_avg.csv'

TEAM_COL = 'TEAM'
STAT_COL = '_2014'
PROJECTION_COLS = ['_AVG', '_ESPN', '_RW', '_RB', '_WIRE',]
CATEGORIES = ['PTS', 'REB', 'AST', '3PM', 'BLK', 'STL']
NUM_PLAYERS = 150 # Number of players to use for main zscore

PLAYERS_TO_REMOVE = ['Paul George', 'Metta World Peace', 'Andrew Bynum']

class PlayerImporter():

    def __init__(self, data_file=DATA_FILE, team_col=TEAM_COL, stat_col=STAT_COL,
            projection_cols=PROJECTION_COLS, remove_players=PLAYERS_TO_REMOVE,
            categories=CATEGORIES, num_players=NUM_PLAYERS):

        self.team_col = team_col
        self.stat_col = stat_col
        self.proj_cols = projection_cols
        self.remove_play = remove_players
        self.cats = categories
        self.num = num_players

        self.df = pd.read_csv(data_file)

    def _create_teams(self):
        team_groups = self.df.groupby(TEAM_COL)
        for name, group in team_groups:
            team = Team(name=name)
            team.save()

    def _create_players(self):
        self.df.apply(self._add_to_db, axis=1)

    def _add_to_db(self, row):
        name = row['PLAYER']
        pos = row['POS']
        rank = row['RANK']
        team = Team.objects(name=row[self.team_col]).first()
        stats = row.filter(regex=self.stat_col + '$').to_dict()
        ranks = row.filter(regex='RANK').to_dict()
        proj = {}
        zscores = {}
        zscores[self.stat_col[1:]] = row.filter(regex=self.stat_col + '_Zscore')
        for col in self.proj_cols:
            proj[col[1:]] = row.filter(regex=col + '$').to_dict()
            zscores[col[1:]] = row.filter(regex=col + '_Zscore').to_dict()

        player = Player(name=name, team=team, pos=pos, rank=rank, ranks=ranks,
                        stats=stats, proj=proj, zscores=zscores)
        player.save()
        return player

    def _clean_data(self):
        df = self.df
        for player in self.remove_play:
            df = df[~df['PLAYER'].str.contains(player)] # take out PG
        self.df = df
        return df

    def _get_top_players(self):
        """ grabs the top self.num of players by zscore the drops the rest
        """
        df = self.df

        first_zscore_col = self.proj_cols[0]
        total_zscore_col = 'TOT' + first_zscore_col + '_Zscore'

        df = self._calc_zscore(df, first_zscore_col)
        df = df.sort(columns=[total_zscore_col], ascending=False)
        df = df[:self.num]
        df = df.drop(df.filter(regex='_Zscore').columns, axis=1)

        return df

    def _calc_zscore(self, df, col_set, calc_big=False):
        total_zscore_col = 'TOT' + col_set + '_Zscore'
        big_zscore_col = 'BIG' + col_set + '_Zscore'
        cols = df.filter(regex=col_set).columns
        # get only our stat columns
        cols = list(set([s + col_set for s in self.cats]) & set(cols))

        for col in cols:
            df[col + '_Zscore'] = (df[col] - df[col].mean())/df[col].std(ddof=0)

        df[total_zscore_col] = df.filter(regex=col_set + '_Zscore').sum(axis=1)
        if calc_big:
            big_cols = [s + '_Zscore' for s in cols]
            big_cols = [col for col in big_cols if not 'AST' in col if not '3P' in col]
            df[big_zscore_col] = df[big_cols].sum(axis=1)
            df['DIFF' + col_set + '_Zscore'] = (df[big_zscore_col] - df[total_zscore_col])

        return df

    def _create_zscores(self):
        df = self.df
        df = self._get_top_players()
        df = self._calc_zscore(df, self.stat_col, calc_big=True)

        for col in self.proj_cols:
            df = self._calc_zscore(df, col, calc_big=True)
        self.df = df
        return df

    def _rank_players(self):
        df = self.df
        total_zscore_col = 'TOT' + self.proj_cols[0] + '_Zscore'
        big_zscore_col = 'BIG' + self.proj_cols[0] + '_Zscore'

        df['RANK'] = df[total_zscore_col].rank(ascending=False)
        df['RANK_BIG'] = df[big_zscore_col].rank(ascending=False)
        df['POS_RANK'] = df.groupby('POS')[total_zscore_col].rank(ascending=False)
        df = df.sort(columns=[total_zscore_col], ascending=False)

        self.df = df
        return df

    def run(self):
        df = self.df

        df = self._clean_data()
        df = self._create_zscores()
        df = self._rank_players()

        self._create_teams()
        self._create_players()



if __name__ == '__main__':
    importer = PlayerImporter()
    importer.run()
    importer.df.to_csv('data.csv')
