#Matching script based on record_linkage_example.py from datamade/dedupe-examples/

import os
import csv
import re
import collections
import logging
import optparse
import numpy
import pandas as pd

import dedupe
from unidecode import unidecode

#%%
def get_twitterdf(filelist=['data/twitter_followers.json']):
    twitterdf=None
    for file in filelist:
        if not twitterdf:
            twitterdf = pd.read_json(file)
            twitterdf['source_file']=file
        else:
            newdf=pd.read_json(file)
            newdf['source_file']=file
            twitterdf.append(newdf,inplace=True)
    return twitterdf

def clean_twitterdf(twitterdf):
    tmptwitterdf=twitterdf[['id','name','screen_name','location','lang','description','source_file']].copy()
                    #,'entities','favourites_count','followers_count','friends_count']]
    tmptwitterdf.rename(columns={'id':'twitter_id','screen_name':'twitter_screen_name'},inplace=True)
    tmptwitterdf['meetup_id']=None
    return tmptwitterdf
def get_meetupdf(filelist=['data/meetup_members.json']):
    meetupdf=None
    for file in filelist:
        if not meetupdf:
            meetupdf = pd.read_json(file)
            meetupdf['source_file']=file
        else:
            newdf=pd.read_json(file)
            newdf['source_file']=file
            meetupdf.append(newdf,inplace=True)
    return meetupdf

def clean_meetupdf(meetupdf):
    meetupdf['twitter_screen_name'] = meetupdf.other_services.map(\
        lambda d:None if 'twitter' not in d else d['twitter']['identifier'][1:])
    countrydf = pd.read_csv('data/iso3166.csv')
    countrydf.index = countrydf.country_id
    meetupdf['country_full'] = meetupdf.country.map(lambda x:countrydf.country.loc[x.upper()])
    meetupdf['location'] = meetupdf.apply(lambda row: row['city'] + ', '+ row['country_full'],axis=1)
    tmpmeetupdf = meetupdf[['id','name','twitter_screen_name','location','lang','bio','source_file']].copy()
    tmpmeetupdf.rename(columns={'id':'meetup_id','bio':'description'},inplace=True)
    tmpmeetupdf['twitter_id']=None
    return tmpmeetupdf
        
twitterdf = get_twitterdf()
tmptwitterdf = clean_twitterdf(twitterdf)
tmptwitterdf.to_csv('tmp/tmptwitter.csv',encoding='utf-8')

meetupdf = get_meetupdf()
tmpmeetupdf = clean_meetupdf(meetupdf)
tmpmeetupdf.to_csv('tmp/tmpmeetup.csv',encoding='utf-8')
#%%   
   
# ## Logging
# dedupe uses Python logging to show or suppress verbose output. Added for convenience.
# To enable verbose logging, run `python examples/csv_example/csv_example.py -v`
optp = optparse.OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)'
                )
(opts, args) = optp.parse_args()
log_level = logging.WARNING 
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG
logging.getLogger().setLevel(log_level)


# ## Setup
settings_file = 'tmp/data_matching_learned_settings'
training_file = 'tmp/data_matching_training.json'

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """

    column = unidecode(column)
    column = re.sub('\n', ' ', column)
    column = re.sub('-', '', column)
    column = re.sub('/', ' ', column)
    column = re.sub("'", '', column)
    column = re.sub(",", '', column)
    column = re.sub(":", ' ', column)
    column = re.sub('  +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    return column

def readData(filename):
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID.
    """

    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            clean_row = dict([(k, preProcess(v)) for (k, v) in row.items()])
            #try :
            #    clean_row['price'] = float(clean_row['price'][1:])
            #except ValueError :
            #    clean_row['price'] = 0
            data_d[filename + str(i)] = dict(clean_row)

    return data_d

print 'importing data ...'
data_1 = readData('tmp/tmptwitter.csv')
data_2 = readData('tmp/tmpmeetup.csv')


# ## Training


if os.path.exists(settings_file):
    print 'reading from', settings_file
    with open(settings_file) as sf :
        linker = dedupe.StaticRecordLink(sf)

else:
    # Define the fields the linker will pay attention to
    #
    # 'name','twitter_screen_name','location','lang','description'
    fields = [
        {'field' : 'name', 'type': 'String', 'has missing' : True },
        {'field' : 'twitter_screen_name', 'type': 'String', 'has missing' : True},
        {'field' : 'location', 'type': 'String', 'has missing' : True},
        {'field' : 'lang', 'type': 'String', 'has missing' : True},
        {'field' : 'description', 'type': 'Text','has missing' : True}]

    # Create a new linker object and pass our data model to it.
    linker = dedupe.RecordLink(fields)
    # To train the linker, we feed it a sample of records.
    linker.sample(data_1, data_2, 150000)

    # If we have training data saved from a previous run of linker,
    # look for it an load it in.
    # __Note:__ if you want to train from scratch, delete the training_file
    if os.path.exists(training_file):
        print 'reading labeled examples from ', training_file
        with open(training_file) as tf :
            linker.readTraining(tf)

    # ## Active learning
    # Dedupe will find the next pair of records
    # it is least certain about and ask you to label them as matches
    # or not.
    # use 'y', 'n' and 'u' keys to flag duplicates
    # press 'f' when you are finished
    print 'starting active labeling...'

    dedupe.consoleLabel(linker)

    linker.train()

    # When finished, save our training away to disk
    with open(training_file, 'w') as tf :
        linker.writeTraining(tf)

    # Save our weights and predicates to disk.  If the settings file
    # exists, we will skip all the training and learning next time we run
    # this file.
    with open(settings_file, 'w') as sf :
        linker.writeSettings(sf)


# ## Blocking

# ## Clustering

# Find the threshold that will maximize a weighted average of our
# precision and recall.  When we set the recall weight to 2, we are
# saying we care twice as much about recall as we do precision.
#
# If we had more data, we would not pass in all the blocked data into
# this function but a representative sample.

print 'clustering...'
linked_records = linker.match(data_1, data_2, 0)

print '# matches found', len(linked_records)

# ## Writing Results

# Write our original data back out to a CSV with a new column called 
# 'Cluster ID' which indicates which records refer to each other.

cluster_membership = {}
cluster_id = None
for cluster_id, (cluster, score) in enumerate(linked_records):
    for record_id in cluster:
        cluster_membership[record_id] = (cluster_id, score)
    

#%%
tmptwitterdf['details']= tmptwitterdf.index.map(lambda x:cluster_membership.get('tmp/tmptwitter.csv'+str(x)))
tmptwitterdf['cluster_id']=tmptwitterdf.details.map(lambda x:None if x is None else x[0])
tmptwitterdf['link_score']=tmptwitterdf.details.map(lambda x:None if x is None else x[1])
tmptwitterdf.drop('details',axis=1,inplace=True)
tmptwitterdf.count()

#%%
tmpmeetupdf['details']= tmpmeetupdf.index.map(lambda x:cluster_membership.get('tmp/tmpmeetup.csv'+str(x)))
tmpmeetupdf['cluster_id']=tmpmeetupdf.details.map(lambda x:None if x is None else x[0])
tmpmeetupdf['link_score']=tmpmeetupdf.details.map(lambda x:None if x is None else x[1])
tmpmeetupdf.drop('details',axis=1,inplace=True)
tmpmeetupdf.count()
#%%
bothdf = tmpmeetupdf.append(tmptwitterdf,ignore_index=True)
bothdf.sort(['cluster_id','source_file'],inplace=True)

#Add a cluster id for unmatched records
nocluster_id = bothdf.cluster_id.isnull()
maxid = int(bothdf.cluster_id.max())
nocluster_num = int(nocluster_id.sum())
bothdf.loc[nocluster_id,'cluster_id'] = range(maxid+1,maxid+1+nocluster_num)

#reordering columns
bothdf = bothdf[['cluster_id','link_score','source_file','meetup_id','twitter_id','name','twitter_screen_name','location','lang','description']]
bothdf.to_csv('output/data_matching_output_full.csv',encoding='utf-8')
gb = bothdf.groupby('cluster_id')
clusterdf = gb[['link_score','meetup_id','twitter_id']].max()
clusterdf['source_1']=gb['source_file'].apply(lambda x: x.iloc[0])
clusterdf['source_2']=gb['source_file'].apply(lambda x: None if len(x)==1 else x.iloc[1])
clusterdf.to_csv('output/clusters.csv')
print "saved output in clusters.csv and data_matching_output_full.csv"