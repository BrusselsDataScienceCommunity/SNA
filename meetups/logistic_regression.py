import numpy
import pandas as pd
from pylab import *
cdict = {'green':   ((0.0, 0.9, 0.9),
                   (1.0, 1.0, 1.0)),
         'blue': ((0.0, 0.9, 0.9),
                   (1.0, 0.9, 0.9)),
         'red':  ((0.0, 1.0, 1.0),
                   (1.0, 0.9, 0.9))}
LightRdBu = matplotlib.colors.LinearSegmentedColormap('LightRdBu', cdict)
numpy.set_printoptions(linewidth=165)

df = pd.read_csv('output/new-old-metrics.csv')
X = df[['interests_members_L2_old','activity_old','connectedness_L2_old']].values
Xlabels = ['interest','activiy','connectedness']
#X = df['connectedness_L2_old'].values
#X = X.reshape((len(X),1))
Y = df['BDSmember_now'].values

from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
model = linear_model.LogisticRegression(fit_intercept=True)
model.fit(X,Y)
#prob = model.predict_proba(df[['interests_members_L2_old','activity_old','connectedness_L2_old']].values)[:,1]
#prob = model.predict_proba(df[['connectedness_L2_old']].values)[:,1]

n_bins = 20
n_var = 3
averages = X.mean(axis=0)

def barplot(ax,iX, xlabel='x', fraction=False):
    ax.set_xlabel(xlabel, fontsize=14, labelpad=0)
    ax.set_ylabel('members (bl) BDS(gr)', fontsize=14,labelpad=0)
    bins = numpy.linspace(X[:,iX].min(),X[:,iX].max()+0.01,n_bins)
    inds = numpy.digitize(X[:,iX],bins)
    #numpy.nan_to_num(binYs)
    if fraction:
        binY_means = [Y[numpy.where(inds==ibin)].mean() for ibin in xrange(len(bins))]
        bar(bins,binY_means,width=bins[1]-bins[0])
        #model = linear_model.LogisticRegression(fit_intercept=True)
        #model = GaussianNB()
        #model.fit(X.reshape((-1,1)),Y)
        x_prob = numpy.ones((n_bins,n_var))
        for i in xrange(n_var): x_prob[:,i] = averages[i]
        x_prob[:,iX]=bins
        proba = model.predict_proba(x_prob)
        plot(bins,proba[:,1],'--')
    else:
        binY_totals = [len(numpy.where(inds==ibin)[0]) for ibin in xrange(len(bins))]
        binY_hits = [Y[numpy.where(inds==ibin)].sum() for ibin in xrange(len(bins))]
        #print bins, binY_totals, binY_hits, bins[1]-bins[0]
        #ax.set_yscale('log')
        bar(bins,binY_totals,width=bins[1]-bins[0],log=True)
        bar(bins,binY_hits,width=bins[1]-bins[0],color='green',log=True)


def scatterplot(ax,iX1,iX2,Xlabel,Ylabel):
    ind=numpy.argsort(Y)
    print len(numpy.where(Y==0)[0])
    ax.set_xlabel(Xlabel, fontsize=14, labelpad=0)
    ax.set_ylabel(Ylabel, fontsize=14,labelpad=0)
    #model = linear_model.LogisticRegression(fit_intercept=True)#GaussianNB()#
    #model.fit(numpy.asarray([X1,X2]).T,Y)
    binsX1 = numpy.linspace(X[:,iX1].min(),X[:,iX1].max()+0.01,n_bins*3)
    binsX2 = numpy.linspace(X[:,iX2].min(),X[:,iX2].max()+0.01,n_bins*3)
    x_prob = numpy.ones((n_bins*3*n_bins*3,n_var))
    for i in xrange(n_var): x_prob[:,i] = averages[i]
    gridx1,gridx2 = numpy.asarray(numpy.meshgrid(binsX1,binsX2))
    x_prob[:,iX1]=numpy.hstack(gridx1)
    x_prob[:,iX2]=numpy.hstack(gridx2)
    proba = model.predict_proba(x_prob)
    ax.pcolor(binsX1, binsX2, proba[:,0].reshape((n_bins*3,n_bins*3)), cmap=LightRdBu, vmin=0, vmax=1)
    ax.scatter(X[:,iX1][ind], X[:,iX2][ind], s=5, c=Y[ind], vmin=-1, vmax=1, lw = 0)#, cmap=BinaryRdBu
    
#for a first assessment this plots each characteristic indvidiually showing how many members in general and how many BSD members exist as a function of characteristic (histogram)
fig = figure(figsize=(8, 6))
for i in xrange(3):
    ax = fig.add_subplot(2,2,i+1)
    barplot(ax,i,Xlabels[i],fraction=False)

#this plot is the quotient of the above histograms for each characteristic. This is the data, that the logistic function is fitted to, and will allow to check the quality of the fit. (well, this were true if only characteristic was fitted at a time)
fig = figure(figsize=(8, 6))
for i in xrange(3):
    ax = fig.add_subplot(2,2,i+1)
    barplot(ax,i,Xlabels[i],fraction=True)

#this is is similar to the first plot but showing two characteristics in a 2d plot (which is the relevant version because sklearn will perform its fit in all three dimensions as we used it)
fig = figure(figsize=(8, 8))
ax = fig.add_subplot(2,2,1)
scatterplot(ax,0,1,Xlabels[0],Xlabels[1])
ax = fig.add_subplot(2,2,2)
scatterplot(ax,1,2,Xlabels[1],Xlabels[2])
ax = fig.add_subplot(2,2,3)
scatterplot(ax,0,2,Xlabels[0],Xlabels[2])

show()
