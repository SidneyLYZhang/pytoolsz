#  ____       _____           _
# |  _ \ _   |_   _|__   ___ | |___ ____
# | |_) | | | || |/ _ \ / _ \| / __|_  /
# |  __/| |_| || | (_) | (_) | \__ \/ /
# |_|    \__, ||_|\___/ \___/|_|___/___|
#        |___/

# Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>
# PyToolsz is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np



class bullet(object):
    def __init__(self, data, fitted = False, limits = None, palette = None) -> None:
        '''
        fitted data: 为已经整理好的
        '''
        self.data = data
        self.__fitdata = data if fitted else None
        self.__limits = limits if fitted else None
        self.__pldata = None
        self.__config = {
            'Font':'Simhei',
            'palette': palette if palette else "green",
            'target_color': '#f7f7f7',
            'bar_color': '#252525',
            'label_color': 'black',
            'keep_label': None, #分类数据顺序
            'pass_zero': True,
            'orientations': 'horizontal', #方向：{'vertical', 'horizontal'}
            'figsize': (12,8),
            'labels': None,
            'formatter': None,
            'axis_label' : None,
            'title' : None,
        }
    def datafitting(self, values = None, index = None, columns = None, aggfunc = 'sum'):
        if self.__fitdata is None:
            self.__fitdata = self.data.pivot_table(values=values,index=index,columns=columns,aggfunc=aggfunc)
        if self.__config['keep_label'] :
            self.__fitdata = self.__fitdata[self.__config['keep_label']]
        if self.__config['pass_zero']:
            for i in self.__fitdata.columns.tolist():
                self.__fitdata.loc[self.__fitdata[i]==0,i] = np.nan
        res = self.__fitdata.describe().T
        res = res[['mean','50%']]
        self.__pldata = list(map(lambda x:list([x[0],*x[1]]),res.iterrows()))
        res = res.describe().loc[["min","25%","75%","max"]]
        if self.__limits is None:
            self.__limits = list(map(lambda x: min(x[1]) if x[0]!="max" else np.ceil(max(x[1])*1.1),res.iterrows()))
        if self.__config["labels"] is None:
            self.__config["labels"] = [' ']*len(self.__limits)
    def config(self,**args):
        self.__config.update(args)
    def heatmap(self):
        '''
        直接使用fitted data数据绘制热力图。
        '''
        plt.figure(figsize=self.__config["figsize"])
        sns.heatmap(self.__fitdata.T,cmap=self.__config["palette"])
    def plot(self, save = None):
            # Determine the max value for adjusting the bar height
            # Dividing by 10 seems to work pretty well
            h = self.__limits[-1] / 10
            plt.rcParams['font.sans-serif'] = [self.__config['Font']]
            # Use the green palette as a sensible default
            if isinstance(self.__config["palette"], str):
                tPalette = sns.light_palette(self.__config["palette"], len(self.__limits), reverse=False)
            else:
                tPalette = self.__config["palette"]
            
            # Must be able to handle one or many data sets via multiple subplots
            if len(self.__pldata) == 1:
                RoCo_Nums = {
                    "sharex" if self.__config['orientations']=='horizontal' else "sharey" : True
                }
                fig, ax = plt.subplots(figsize=self.__config["figsize"], **RoCo_Nums)
            else:
                RoCo_Nums = {
                    "nrows" if self.__config['orientations']=='horizontal' else "ncols" : len(self.__pldata),
                    "sharex" if self.__config['orientations']=='horizontal' else "sharey" : True
                }
                fig, axarr = plt.subplots(figsize=self.__config["figsize"], **RoCo_Nums)

            # Add each bullet graph bar to a subplot
            for idx, item in enumerate(self.__pldata):
                
                # Get the axis from the array of axes returned when the plot is created
                if len(self.__pldata) > 1:
                    ax = axarr[idx]

                # Formatting to get rid of extra marking clutter
                ax.set_aspect('equal')
                if self.__config['orientations']=='horizontal':
                    ax.set_yticklabels([item[0]])
                    ax.set_yticks([1])
                else:
                    ax.set_xticklabels([item[0]])
                    ax.set_xticks([1])
                ax.spines['bottom'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)

                prev_limit = 0
                for idx2, lim in enumerate(self.__limits):
                    # Draw the bar
                    if self.__config['orientations']=='horizontal':
                        ax.barh([1], lim - prev_limit, left=prev_limit, height=h,
                                color=tPalette[idx2])
                    else:
                        ax.bar([1],lim - prev_limit, bottom=prev_limit, width=h,
                               color=tPalette[idx2])
                    prev_limit = lim
                rects = ax.patches
                # The last item in the list is the value we're measuring
                # Draw the value we're measuring
                if self.__config['orientations']=='horizontal':
                    ax.barh([1], item[1], height=(h / 3), color=self.__config["bar_color"])
                else:
                    ax.bar([1], item[1], width=(h / 3), color=self.__config["bar_color"])

                # Need the ymin and max in order to make sure the target marker
                # fits
                if self.__config['orientations']=='horizontal':
                    ymin, ymax = ax.get_ylim()
                    ax.vlines(
                        item[2], ymin * .9, ymax * .9, linewidth=1.5, color=self.__config["target_color"])
                else:
                    xmin, xmax = ax.get_xlim()
                    ax.hlines(
                        item[2], xmin*0.9, xmax*0.9, linewidth=1.5, color=self.__config["target_color"])

            # Now make some labels
            if self.__config["labels"] is not None:
                for rect, label in zip(rects, self.__config["labels"]):
                    if self.__config['orientations']=='horizontal':
                        height = rect.get_height()
                        ax.text(
                            rect.get_x() + rect.get_width() / 2,
                            -height * .4,
                            label,
                            ha='center',
                            va='bottom',
                            color=self.__config["label_color"])
                    else:
                        width = rect.get_width()
                        ax.text(
                            -width * .4,
                            rect.get_y() + rect.get_height() / 2,
                            label,
                            ha='left',
                            va='center',
                            color=self.__config["label_color"])
            if self.__config["formatter"]:
                if self.__config['orientations']=='horizontal':
                    ax.xaxis.set_major_formatter(self.__config["formatter"])
                else:
                    ax.yaxis.set_major_formatter(self.__config["formatter"])
            if self.__config["axis_label"]:
                if self.__config['orientations']=='horizontal':
                    ax.set_xlabel(self.__config["axis_label"])
                else:
                    ax.set_ylabel(self.__config["axis_label"])
            if self.__config["title"]:
                fig.suptitle(self.__config["title"], fontsize=14)
            WHspace = {"hspace" if self.__config['orientations']=='horizontal' else "wspace":0}
            fig.subplots_adjust(**WHspace)
