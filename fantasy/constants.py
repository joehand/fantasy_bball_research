import os


NUM_TEAMS = 12
PLAYERS_PER_TEAM = 10
BENCH_PLAYERS = 2

STAT_CATS = ['PTS', 'REB', 'BLK','STL', 'AST', '3PM']
POS = ['PG', 'SG', 'SF', 'PF', 'C']
DRAFT_POS = ['PG', 'SG', 'SF', 'PF', 'C', 'F/C', 'G', 'UTIL', 'BENCH']

TOTAL_DOLLARS = 200 * NUM_TEAMS
TOTAL_PLAYERS = PLAYERS_PER_TEAM * NUM_TEAMS


# Needs to be public and output=csv. Also the sheet we want has to be first.
DRAFT_SHEET_URL = 'https://docs.google.com/spreadsheet/ccc?key=19YpHBaqzp4uccm1q7BgT3ssC_U_TtPaP705xUsHIxN0&gid=1178982124&output=csv'

PLOT_SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'templates', 'plots'))

PLOT_DEFAULTS = {
    'all' : {
        'title' : 'Total Z-Score (Average Projection)',
        'x_var' : 'rank',
        'y_var' : 'zscores_AVG_TOT_AVG_Zscore',
        'y_var2' : 'zscores_2014_TOT_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_TOT',
        'group' : 'pos',
        'drafted' : 'drafted',
        'save_file' : 'all.html',
    },
    'undrafted_all' : {
        'title' : 'Undrafted Total Z-Score (Average Projection)',
        'x_var' : 'rank',
        'y_var' : 'zscores_AVG_TOT_AVG_Zscore',
        'y_var2' : 'zscores_2014_TOT_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_TOT',
        'group' : 'pos',
        'drafted' : False,
        'save_file' : 'undrafted_all.html',
    },
    'big' : {
        'title' : 'No AST/3PM Z-Score (Average Projection)',
        'x_var' : 'ranks_RANK_BIG',
        'y_var' : 'zscores_AVG_BIG_AVG_Zscore',
        'y_var2' : 'zscores_2014_BIG_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_BIG',
        'group' : 'pos',
        'drafted' : 'drafted',
        'save_file' : 'big.html',
    },
    'undrafted_big' : {
        'title' : 'Undrafted No AST/3PM Z-Score (Average Projection)',
        'x_var' : 'ranks_RANK_BIG',
        'y_var' : 'zscores_AVG_BIG_AVG_Zscore',
        'y_var2' : 'zscores_2014_BIG_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_BIG',
        'group' : 'pos',
        'drafted' : False,
        'save_file' : 'undrafted_big.html',
    },
    'diff' : {
        'title' : 'Z-Score Difference (Average Projection)',
        'x_var' : 'ranks_RANK_BIG',
        'y_var' : 'zscores_AVG_DIFF_AVG_Zscore',
        'y_var2' : 'zscores_2014_DIFF_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_DIFF',
        'group' : 'pos',
        'drafted' : 'drafted',
        'save_file' : 'diff.html',
    },
    'undrafted_diff' : {
        'title' : 'Undrafted Z-Score Difference (Average Projection)',
        'x_var' : 'ranks_RANK_BIG',
        'y_var' : 'zscores_AVG_DIFF_AVG_Zscore',
        'y_var2' : 'zscores_2014_DIFF_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_DIFF',
        'group' : 'pos',
        'drafted' : False,
        'save_file' : 'undrafted_diff.html',
    },
    'price' : {
        'title' : 'Price vs Total Z Score',
        'x_var' : 'price',
        'y_var' : 'zscores_AVG_TOT_AVG_Zscore',
        'y_var2' : 'zscores_2014_TOT_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_TOT',
        'group' : 'pos',
        'drafted' : 'drafted',
        'save_file' : 'price.html',
        'type':'price',
        'undrafted_x_var' : 'live_cost_tot',
    },
    'undrafted_price' : {
        'title' : 'Undrafted Price vs Total Z Score',
        'x_var' : 'live_cost_tot',
        'y_var' : 'zscores_AVG_TOT_AVG_Zscore',
        'y_var2' : 'zscores_2014_TOT_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_TOT',
        'group' : 'pos',
        'drafted' : False,
        'save_file' : 'undrafted_price.html',
        'type':'price',
    },
    'price_big' : {
        'title' : 'Price vs Big Z Score',
        'x_var' : 'price',
        'y_var' : 'zscores_AVG_BIG_AVG_Zscore',
        'y_var2' : 'zscores_2014_BIG_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_BIG',
        'group' : 'pos',
        'drafted' : 'drafted',
        'save_file' : 'price_big.html',
        'type':'price',
        'undrafted_x_var' : 'live_cost_big',
    },
    'undrafted_price_big' : {
        'title' : 'Undrafted Price vs Big Z Score',
        'x_var' : 'live_cost_big',
        'y_var' : 'zscores_AVG_BIG_AVG_Zscore',
        'y_var2' : 'zscores_2014_BIG_2014_Zscore',
        'y_err_regex' : '^zscores_([a-zA-Z]+)_BIG',
        'group' : 'pos',
        'drafted' : False,
        'save_file' : 'undrafted_price_big.html',
        'type':'price',
    },
}

PLOT_TOOLTIP = """ <table class="player table table-condensed">
                      <tr><th colspan=2>{name}</th></tr>
                      <tr class="rank"><th>{pos} Rank</th><td>{ranks_POS_RANK:1.0f}</td></tr>
                      <tr><th>PTS</th><td>{proj_AVG_PTS_AVG}</td></tr>
                      <tr><th>REB</th><td>{proj_AVG_REB_AVG}</td></tr>
                      <tr><th>STL</th><td>{proj_AVG_STL_AVG}</td></tr>
                      <tr><th>BLK</th><td>{proj_AVG_BLK_AVG}</td></tr>
                      <tr><th>AST</th><td>{proj_AVG_AST_AVG}</td></tr>
                      <tr><th>3PM</th><td>{proj_AVG_3PM_AVG}</td></tr>
                     </table>"""
