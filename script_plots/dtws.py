from random import random
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from common import *
import numpy as np
import os
import random

def process_csv(file):
    df = pd.read_csv(file)

    names = list(df['t1'].values) + list(df['t2'].values)
    print(set(names))
    data = dict(name=file, count=len(names), names=set(names), difs=list(df['diff'].values))

    return data


def plot_zero(datas):
    
    latexify(fig_height=2, fig_width=8.5, font_size=11, tick_size=10)
    fig, ax = plt.subplots()
    format_axes(ax, hide=['top', 'right', 'bottom'], show=['left'])

    non_zero_ratio = [ 1 - 1*len([i for i in d if i == 0])/len(d) for d in datas ]

    # Filter only those with some zero
    non_zero_ratio = filter(lambda x: x != 1.0, non_zero_ratio)
    non_zero_ratio = sorted(non_zero_ratio, reverse=True)
    non_zero_ratio = list(non_zero_ratio)

    

    ax.bar(list(range(len(non_zero_ratio))), non_zero_ratio)
    ax.bar(list(range(len(non_zero_ratio))), [1-x for x in non_zero_ratio], bottom=non_zero_ratio, color=[0.1,0.1,0.1, 0.1])
    ax.set_xticks([])
    ax.set_ylabel("Non-zero ratio")

    print(len(non_zero_ratio))

    plt.savefig("../plots/non_zero_ratio.pdf")

def plot_distribs(datas, name="dtw_distrib"):


    latexify(fig_height=3.1, fig_width=8.5, font_size=10, tick_size=10)
    fig, ax = plt.subplots()

    format_axes(ax, hide=['top', 'right'], show=['left', 'bottom'])
    xPos = np.arange(len(datas))
    CTEs = []
    error = []
    FROM  = 0

    baseline = -1
    baselineName = ''
    baselinemean = 0
    baselineData = []

    means = []
    vals = []
    names = []

    def format(v):
        return v

    for i,k in enumerate(datas):#
        try:
            means.append(np.median([format(v) for v in k[FROM:] if not np.isnan(v)]))
            vals.append([format(v) for v in k[FROM:] if not np.isnan(v)])
            names.append(f"{i}")
        except Exception as e:
            print(e)
    #print(means, vals, names)
    #if baseline == -1:
        
    #    dataRaw = [(k, v[1]) for k, v in data.items()]
    #    dataRaw = dataRaw[0]
    #    baseline = dataRaw[0]
    #    baselinemean = np.median([format(v) for v in dataRaw[1]])
    #    baselineData = [format(v) for v in dataRaw[1]]
    #    vals = vals[1:]
        
    means = sorted(means, reverse=True)
    means = means
    vals = sorted(vals, key= lambda x: np.median(x), reverse=True)

    vals = vals

    def filt(q75, q25, val, iqrange=1.5):
        
        iqr = q75 - q25
        cut_off = iqr*iqrange
        lower, upper = q25 - cut_off, q75 + cut_off
        return lower <= val <= upper

    def getDataToDraw(v, low=25, high=75, iqrange=1.5):
        # print(v)
        quantiles75 = np.percentile(v, high )
        quantiles25 = np.percentile(v, low )

        median = np.median(v)



        iqr = quantiles75 - quantiles25
        cut_off = iqr*iqrange
        lower, upper = quantiles25 - cut_off, quantiles75 + cut_off

        # print(quantiles25, quantiles75, median, cut_off)        

        data = [m for m in v if lower <= m <= upper]

        return median, quantiles25, quantiles75, lower, upper, data, min(data), max(data)

    LINEWIDTH=1.2
    SCATTER_SIZE=7
    SCALE=100
    DIST_ALPHA=0.5

    ax.set_xticks([])
    #ax.violinplot(vals, showmeans=True)#, widths=[1.2]*len(vals))
    ax.set_ylabel("TraceDiff value")
    S=2.0
    vals = sorted(vals, key=lambda x: len(x), reverse=True)
    for i, data in enumerate(vals):
        xs = [ 10*i + 0*(0.5 - random.random()) for _ in range(len(data)) ]
        # print(xs)
        ax.scatter(xs, data, alpha=0.6, color=[0.8,0.8,0.8,0], edgecolors='C0', s=S)
        ax.vlines(10*i,  ymin=0, ymax=max(data), alpha=0.3, color=[0.8,0.8,0.8,0.1])
        #ax.scatter([i], [0], edgecolors='C1', color=[0.8,0.8,0.8,0])
    #ax.barh(y=0, color='C1', width=len(vals), left=0)
    #ax.set_ylim(0)
    ax.set_yscale('log')
    #for i,v in enumerate(vals):
    #    COLOR = 'C0' # if i > 0 else 'C3'
    #    COLOR3 = 'gray'
    #    COLOR2 = 'C6'
    #    median, quantiles25, quantiles75, lower, upper, data, m , M = getDataToDraw(v, low=25, high=75)
    #    ax.plot([SCALE*i, SCALE*i], [quantiles75, M], color=COLOR3, linewidth=LINEWIDTH, alpha=0.6*DIST_ALPHA)
    #    ax.plot([SCALE*i, SCALE*i], [quantiles75, quantiles25], color=COLOR3, linewidth=2.2*LINEWIDTH, alpha=1.2*DIST_ALPHA)
    #    ax.plot([SCALE*i, SCALE*i], [m, quantiles25], color=COLOR3, linewidth=LINEWIDTH, alpha=0.6*DIST_ALPHA)
    #    ax.scatter([SCALE*i], [median], color=COLOR, s = SCATTER_SIZE, zorder=10)
    plt.tight_layout()
    plt.savefig(f"../plots/{name}.png")

def plot_grama(data, name="name"):
    latexify(fig_height=3, fig_width=12.5, font_size=11.5, tick_size=11.5)
    fig, ax = plt.subplots()

    format_axes(ax, hide=['top', 'right'], show=['left', 'bottom'])
    xPos = np.arange(len(datas))
    CTEs = []
    error = []
    FROM  = 0

    baseline = -1
    baselineName = ''
    baselinemean = 0
    baselineData = []

    means = []
    vals = []
    names = []

    def format(v):
        return v

    for i,k in enumerate(datas):#
        try:
            means.append(np.median([format(v) for v in k[FROM:] if not np.isnan(v)]))
            vals.append([format(v) for v in k[FROM:] if not np.isnan(v)])
            names.append(f"{i}")
        except Exception as e:
            print(e)
    #print(means, vals, names)
    #if baseline == -1:
        
    #    dataRaw = [(k, v[1]) for k, v in data.items()]
    #    dataRaw = dataRaw[0]
    #    baseline = dataRaw[0]
    #    baselinemean = np.median([format(v) for v in dataRaw[1]])
    #    baselineData = [format(v) for v in dataRaw[1]]
    #    vals = vals[1:]
        
    means = sorted(means, reverse=True)
    means = means
    vals = sorted(vals, key= lambda x: np.median(x), reverse=True)

    vals = vals

    def filt(q75, q25, val, iqrange=1.5):
        
        iqr = q75 - q25
        cut_off = iqr*iqrange
        lower, upper = q25 - cut_off, q75 + cut_off
        return lower <= val <= upper

    def getDataToDraw(v, low=25, high=75, iqrange=1.5):
        # print(v)
        quantiles75 = np.percentile(v, high )
        quantiles25 = np.percentile(v, low )

        median = np.median(v)



        iqr = quantiles75 - quantiles25
        cut_off = iqr*iqrange
        lower, upper = quantiles25 - cut_off, quantiles75 + cut_off

        # print(quantiles25, quantiles75, median, cut_off)        

        data = [m for m in v if lower <= m <= upper]

        return median, quantiles25, quantiles75, lower, upper, data, min(data), max(data)

    LINEWIDTH=1.2
    SCATTER_SIZE=7
    SCALE=100
    DIST_ALPHA=0.5

    ax.set_xticks([])
    #ax.violinplot(vals, showmeans=True)#, widths=[1.2]*len(vals))
    ax.set_ylabel("dt\_dyn value")
    S=150
    for i, data in enumerate(vals):
        ax.scatter([i]*len(data), data, alpha=0.5, color=[0.8,0.8,0.8,0], edgecolors='C0', s=S/len(data))
        #ax.scatter([i], [0], edgecolors='C1', color=[0.8,0.8,0.8,0])
    #ax.barh(y=0, color='C1', width=len(vals), left=0)
    #ax.set_ylim(0)
    ax.set_yscale('log')
    #for i,v in enumerate(vals):
    #    COLOR = 'C0' # if i > 0 else 'C3'
    #    COLOR3 = 'gray'
    #    COLOR2 = 'C6'
    #    median, quantiles25, quantiles75, lower, upper, data, m , M = getDataToDraw(v, low=25, high=75)
    #    ax.plot([SCALE*i, SCALE*i], [quantiles75, M], color=COLOR3, linewidth=LINEWIDTH, alpha=0.6*DIST_ALPHA)
    #    ax.plot([SCALE*i, SCALE*i], [quantiles75, quantiles25], color=COLOR3, linewidth=2.2*LINEWIDTH, alpha=1.2*DIST_ALPHA)
    #    ax.plot([SCALE*i, SCALE*i], [m, quantiles25], color=COLOR3, linewidth=LINEWIDTH, alpha=0.6*DIST_ALPHA)
    #    ax.scatter([SCALE*i], [median], color=COLOR, s = SCATTER_SIZE, zorder=10)
    plt.tight_layout()
    plt.savefig(f"../plots/{name}.png")

if __name__ == '__main__':
    datas = [ process_csv(f"{sys.argv[1]}/{f}") for f in os.listdir(sys.argv[1]) ]
    print([d['count'] for d in datas])
    datas = [d['difs'] for d in datas]
    #plot_zero([ d for d in datas if d if len(d) > 0])
    datas = sorted(datas, key=lambda x: len(x), reverse=True)
    print([len(d) for d in datas])
    
    datas = [ d for d in datas if d if len(d) > 2]
    print(len(datas))
    datas = sorted(datas, key=lambda x: len(x), reverse=True)

    # More than one variant
    middle = len(datas)/3
    middle = int(middle)
    plot_distribs(datas[:middle], name="plot_distribs1")
    print(datas[middle])
    plot_distribs(datas[middle:2*middle], name="plot_distribs2")
    plot_distribs(datas[2*middle:], name="plot_distribs3")