import os

import mpld3
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame

from ..utils import async

sns.set_style("ticks")
sns.set_context("poster")
flatui = ["#34495e", "#3498db","#9b59b6", "#e74c3c", "#2ecc71", "#95a5a6",]
sns.set_palette(flatui)

DEFAULTS = {
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
}

DISPLAY_STRING = """ <table class="player table table-condensed">
                      <tr><th colspan=2>{name}</th></tr>
                      <tr class="rank"><th>{pos} Rank</th><td>{ranks_POS_RANK:1.0f}</td></tr>
                      <tr><th>PTS</th><td>{proj_AVG_PTS_AVG}</td></tr>
                      <tr><th>REB</th><td>{proj_AVG_REB_AVG}</td></tr>
                      <tr><th>STL</th><td>{proj_AVG_STL_AVG}</td></tr>
                      <tr><th>BLK</th><td>{proj_AVG_BLK_AVG}</td></tr>
                      <tr><th>AST</th><td>{proj_AVG_AST_AVG}</td></tr>
                      <tr><th>3PM</th><td>{proj_AVG_3PM_AVG}</td></tr>
                     </table>"""

SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates', 'plots'))

@async
def update_plots_async( players):
    for key in DEFAULTS:
        create_plot(players, plot=key)

def update_all_plots(players):
    update_plots_async(players)

def create_plot(players, defaults=DEFAULTS, plot='all'):
    title = defaults[plot]['title']
    x_var = defaults[plot]['x_var']
    y_var = defaults[plot]['y_var']
    y_var2 = defaults[plot]['y_var2']
    y_err_regex = defaults[plot]['y_err_regex']
    group = defaults[plot]['group']
    drafted = defaults[plot]['drafted']
    save_file = defaults[plot]['save_file']

    print('creating plot {}'.format(plot))

    if drafted == False:
        show_draft = False
        drafted = 'drafted'
    else:
        show_draft = True

    player_list = []
    for player in players:
        player_list.append(player.flatten())
    df = DataFrame(player_list)

    df = df.sort(y_var, ascending=False)
    fig, ax = plt.subplots()
    elements = []
    labels=[]
    for name, big_group in df.groupby(group):
        positions = []
        color=next(ax._get_lines.color_cycle)
        for drafted_name, group in big_group.groupby(drafted):
            x = group[x_var]
            y = group[y_var]
            y2 = group[y_var2]
            yerr = [group[y_var] - group.filter(regex=y_err_regex).min(axis=1),
                            group.filter(regex=y_err_regex).max(axis=1) - group[y_var]]

            if drafted_name:
                if show_draft:
                    element = ax.scatter(x,y, color=color,
                                         s=60, alpha=0.6, marker='D')
                    element2 = ax.scatter(x,y2, color=color,
                                         s=90, alpha=0.5, marker='+')
                    ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                    positions.append(element)
                    positions.append(element2)

                    players = list(group.apply(lambda x: DISPLAY_STRING.format(**x),axis=1))
            else:
                element = ax.scatter(x,y, color=color,
                                     s=90, alpha=0.2, marker='o')
                element2 = ax.scatter(x,y2, color=color,
                                     s=90, alpha=0.5, marker='+')
                ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                positions.append(element)
                positions.append(element2)

                players = list(group.apply(lambda x: DISPLAY_STRING.format(**x),axis=1))



            mpld3.plugins.connect(fig, mpld3.plugins.PointHTMLTooltip(element, players,
                                                           voffset=-75, hoffset=10))

        elements.append(positions)
        labels.append(name)

    ax.set_title(title)
    ax.set_xlim(0,(df[x_var].max() + 10))
    mpld3.plugins.connect(fig, mpld3.plugins.InteractiveLegendPlugin(elements, labels))
    mpld3.save_html(fig, SAVE_DIR + '/' + save_file)
    return save_file
