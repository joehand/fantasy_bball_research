import os

import mpld3
import matplotlib.pyplot as plt
import seaborn as sns

from pandas import DataFrame

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
}

SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates', 'plots'))


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
                element = ax.scatter(x,y, color=color,
                                     s=60, alpha=0.6, marker='D')
                element2 = ax.scatter(x,y2, color=color,
                                     s=90, alpha=0.5, marker='+')
                ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                positions.append(element)
                positions.append(element2)
            else:
                element = ax.scatter(x,y, color=color,
                                     s=90, alpha=0.2, marker='o')
                element2 = ax.scatter(x,y2, color=color,
                                     s=90, alpha=0.5, marker='+')
                ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                positions.append(element)
                positions.append(element2)

            display_string = """ <table class="player">
                                  <tr><th colspan=2>{name}</th></tr>
                                  <tr class="rank"><th>{pos} Rank</th><td>{ranks_POS_RANK:1.0f}</td></tr>
                                  <tr><th colspan=2>Projections</th></tr>
                                  <tr><th>MIN</th><td>{proj_AVG_MIN_AVG}</td></tr>
                                  <tr><th>PTS</th><td>{proj_AVG_PTS_AVG}</td></tr>
                                  <tr><th>REB</th><td>{proj_AVG_REB_AVG}</td></tr>
                                  <tr><th>AST</th><td>{proj_AVG_AST_AVG}</td></tr>
                                  <tr><th>STL</th><td>{proj_AVG_STL_AVG}</td></tr>
                                  <tr><th>BLK</th><td>{proj_AVG_BLK_AVG}</td></tr>
                                  <tr><th>3PM</th><td>{proj_AVG_3PM_AVG}</td></tr>
                                 </table>"""
            players = list(group.apply(lambda x: display_string.format(**x),axis=1))

            mpld3.plugins.connect(fig, mpld3.plugins.PointHTMLTooltip(element, players,
                                                           voffset=-25, hoffset=10))

        elements.append(positions)
        labels.append(name)

    ax.set_title(title)
    ax.set_xlim(0,(df[x_var].max() + 10))
    mpld3.plugins.connect(fig, mpld3.plugins.InteractiveLegendPlugin(elements, labels))
    mpld3.save_html(fig, SAVE_DIR + '/' + save_file)
    return save_file
