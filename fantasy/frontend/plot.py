import os

import mpld3
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame

from ..constants import *
from ..utils import async

sns.set_style("ticks")
sns.set_context("poster")
flatui = ["#34495e", "#3498db","#9b59b6", "#e74c3c", "#2ecc71", "#95a5a6",]
sns.set_palette(flatui)

@async
def update_plots_async( players):
    for key in PLOT_DEFAULTS:
        create_plot(players, plot=key)

def update_all_plots(players):
    update_plots_async(players)

def create_plot(players, defaults=PLOT_DEFAULTS, plot='all'):
    title = defaults[plot]['title']
    x_var = defaults[plot]['x_var']
    y_var = defaults[plot]['y_var']
    y_var2 = defaults[plot]['y_var2']
    y_err_regex = defaults[plot]['y_err_regex']
    group = defaults[plot]['group']
    drafted = defaults[plot]['drafted']
    save_file = defaults[plot]['save_file']
    if 'type' in defaults[plot]:
        type = defaults[plot]['type']
    else:
        type = None

    if 'undrafted_x_var' in defaults[plot]:
        undrafted_x_var = defaults[plot]['undrafted_x_var']
    else:
        undrafted_x_var = None


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
                    ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                    positions.append(element)

                    if type != 'price':
                        element2 = ax.scatter(x,y2, color=color,
                            s=90, alpha=0.5, marker='+')
                        positions.append(element2)

                    players = list(group.apply(lambda x: PLOT_TOOLTIP.format(**x),axis=1))

                    mpld3.plugins.connect(fig, mpld3.plugins.PointHTMLTooltip(element, players,
                                                                               voffset=-75, hoffset=10))
            else:
                if undrafted_x_var: #special x var for undrafted price
                    x = group[undrafted_x_var]
                element = ax.scatter(x,y, color=color,
                                     s=90, alpha=0.2, marker='o')
                ax.errorbar(x,y,yerr=yerr, linestyle="None", lw='1',color=color, )
                positions.append(element)

                if type != 'price':
                    element2 = ax.scatter(x,y2, color=color,
                            s=90, alpha=0.5, marker='+')
                    positions.append(element2)

                players = list(group.apply(lambda x: PLOT_TOOLTIP.format(**x),axis=1))

                mpld3.plugins.connect(fig, mpld3.plugins.PointHTMLTooltip(element, players,
                                                                           voffset=-75, hoffset=10))




        elements.append(positions)
        labels.append(name)

    ax.set_title(title)
    if type == 'price':
        ax.set_xlim((df[x_var].max()+1), 0) # hard axis on price, reversed
    else:
        ax.set_xlim(0,(df[x_var].max() + 10))
    mpld3.plugins.connect(fig, mpld3.plugins.InteractiveLegendPlugin(elements, labels))
    mpld3.save_html(fig, PLOT_SAVE_DIR + '/' + save_file)
    return save_file
