import numpy
import pandas as pd
from pylab import *

numpy.set_printoptions(linewidth=165)

df = pd.read_csv('output/new-old-metrics.csv')
X = df[['interests_members_L2_old','activity_old','connectedness_L2_old']].values
Xlabels = ['interest','activiy','connectedness']
#X = df['connectedness_L2_old'].values
#X = X.reshape((len(X),1))
Y = df['BDSmember_now'].values

from sklearn import linear_model
model = linear_model.LogisticRegression(fit_intercept=True)
model.fit(X,Y)
#prob = model.predict_proba(df[['interests_members_L2_old','activity_old','connectedness_L2_old']].values)[:,1]
#prob = model.predict_proba(df[['connectedness_L2_old']].values)[:,1]

n_bins = 20

def barplot(ax,X, xlabel='x', fraction=False):
    ax.set_xlabel(xlabel, fontsize=14, labelpad=0)
    ax.set_ylabel('members (bl) BDS(gr)', fontsize=14,labelpad=0)
    bins = numpy.linspace(X.min(),X.max(),n_bins)
    inds = numpy.digitize(X,bins)
    #numpy.nan_to_num(binYs)
    if fraction:
        binY_means = [Y[numpy.where(inds==ibin)].mean() for ibin in xrange(len(bins))]
        bar(bins,binY_means,width=bins[1]-bins[0])
    else:
        binY_totals = [len(numpy.where(inds==ibin)[0]) for ibin in xrange(len(bins))]
        binY_hits = [Y[numpy.where(inds==ibin)].sum() for ibin in xrange(len(bins))]
        print bins, binY_totals, binY_hits, bins[1]-bins[0]
        #ax.set_yscale('log')
        bar(bins,binY_totals,width=bins[1]-bins[0],log=True)
        bar(bins,binY_hits,width=bins[1]-bins[0],color='green',log=True)

def scatterplot(ax,X1,X2,Xlabel,Ylabel):
    ind=numpy.argsort(Y)
    print len(numpy.where(Y==0)[0])
    ax.set_xlabel(Xlabel, fontsize=14, labelpad=0)
    ax.set_ylabel(Ylabel, fontsize=14,labelpad=0)
    ax.scatter(X1[ind], X2[ind], s=5, c=Y[ind], vmin=-1, vmax=1, lw = 0,alpha=0.4)#, cmap=BinaryRdBu

fig = figure(figsize=(8, 6))
for i in xrange(3):
    ax = fig.add_subplot(2,2,i+1)
    barplot(ax,X[:,i],Xlabels[i],fraction=False)
fig = figure(figsize=(8, 6))
for i in xrange(3):
    ax = fig.add_subplot(2,2,i+1)
    barplot(ax,X[:,i],Xlabels[i],fraction=True)
fig = figure(figsize=(8, 8))
ax = fig.add_subplot(2,2,1)
scatterplot(ax,X[:,0],X[:,1],Xlabels[0],Xlabels[1])
ax = fig.add_subplot(2,2,2)
scatterplot(ax,X[:,1],X[:,2],Xlabels[1],Xlabels[2])
ax = fig.add_subplot(2,2,3)
scatterplot(ax,X[:,0],X[:,2],Xlabels[0],Xlabels[2])

show()
