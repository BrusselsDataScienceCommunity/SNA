from sliced_graph import *
import networkx as nx
import json
import os
import cPickle as pickle
import pandas as pd
from collections import defaultdict
import datetime

# Construct full Meetup graph
def construct_meetup_graph(groups,topics,members,events):
    G = nx.Graph()

    #Create nodes
    for group in groups:
        G.add_node(('group',group['id'])) # Group
    for event in events:
        G.add_node(('event',event),date=datetime.datetime.fromtimestamp(events[event]['time']/1e3)) # Event
    for member in members:
        G.add_node(('member',member)) # Member
    for key in topics:
        G.add_node(('topic',key)) # Topic

    #Create edges:
    for group in groups:
        for key in group['event_keys']:
            G.add_edge(('event',key),('group',group['id']),etype='event of')
        for key,date in zip(group['member_keys'],group['join_date']):
            G.add_edge(('member',key),('group',group['id']),etype='member of',date=date)
        for key in group['topic_keys']:
            G.add_edge(('topic',key),('group',group['id']),etype='topic of')
    for event_key in events:
        for member_key in events[event_key]['member_keys']:
            G.add_edge(('member',member_key),('event',event_key),etype='rsvp')

    for key in members:
        if 'topics' in members[key]:
            for topic in members[key]['topics']:
                G.add_edge(('member',key),('topic',topic['id']),etype='interested in')
    return G


try:
    print 'Loading meetup data'
    groups = pickle.load(open('pickle/groups.pkl', 'r'))
    topics = pickle.load(open('pickle/topics.pkl', 'r'))
    members = pickle.load(open('pickle/members.pkl', 'r'))
    events = pickle.load(open('pickle/events.pkl', 'r'))
except:
    raise Exception('Problem reading pickles, rerun extract_pickle.py!')

groupsdict = {}
for group in groups:
    groupsdict[group['id']] = group
#print '-loading members'
#members = extract_members(groups)


picklefile = 'pickle/sgraph.pkl'
if not os.path.isfile(picklefile):
    print 'First time running this script!'
    print '-constructing full metup graph'
    G = construct_meetup_graph(groups,topics,members,events)
    print '-computing matrices and slices...'
    sgraph = Sliced_graph()
    sgraph.compute_slice_matrices(G)
    sgraph.to_pickle(picklefile)
    print '-saved slices'
else:
    print 'skipping slice computations. To recompute, delete pickle folder.'
    print 'loading matrices and slices from pickle'
    sgraph = read_pickle(picklefile)

#Find the BruDataSci meetup
for idx,n in enumerate(sgraph.OrderedNodes):
    if n[0]=='group':
        if groupsdict[n[1]]['name']=='Brussels Data Science Meetup':
            BDSnode = n
            BDS = groupsdict[n[1]]
            BDSidx = idx
            break

N = len(sgraph.OrderedNodes)

#Initialize vector on the Brussels Data Science group
sgraph.v0 = sgraph.node_to_vector(BDSnode)

# Metrics defined by edge paths 
#   membership = members of groups which share members with BruDataSci
#   interests = Being interested in the same topics as BruDataSci
#   interests_member = Being interested in the same topics as members of BruDataSci
#   *_L2 : same as * but with L2 weighting before and after crossing each edge (+ final L2 normalization)
L2_metrics = {
    'connectedness_L2':{
        'edge_sequence':['member of','member of','member of'],
        'preprocess' : procs['L2'],
        'postprocess' : procs['L2'],
        'norm' : norms['L2']},         
    'interests_L2':{
        'edge_sequence':['topic of','interested in'],
        'preprocess' : procs['L2'],
        'postprocess' : procs['L2'],
        'norm' : norms['L2']},
    'interests_members_L2':{
        'edge_sequence':['member of','interested in','interested in'],
        'preprocess' : procs['L2'],
        'postprocess' : procs['L2'],
        'norm' : norms['L2']},
    'activity_L2':{
        'edge_sequence':['member of','rsvp','rsvp'],
        'preprocess' : procs['L2'],
        'postprocess' : procs['L2'],
        'norm' : norms['L2']},
    'BDSmember':{
        'edge_sequence':['member of']}}
    #'attendee_interest':{'edge_sequence':['event of','rsvp','interested in','interested in']},


BDStopics = len(BDS['topics'])
custom_proc = lambda v,Degs : v / (Degs - v + BDStopics)

kris_metrics = {
    'connectedness': {
        'edge_sequence':['member of','member of','member of']},
    'activity':{'edge_sequence':['member of','rsvp','rsvp']},
    'interests':{
        'edge_sequence':['topic of','interested in'],
        'postprocess':[procs['noprocess'],custom_proc]}}

other_metrics = {
    #Input other metrics here
}

# Create a dataframe to view the output
df = pd.DataFrame({'id':[m for m in members]})
df['name']=df.id.map(lambda x:members[x]['name'])
df['BruDataSci_member'] = df.id.map(lambda x: x in BDS['member_keys'])
print 'computing metrics'
all_metrics = L2_metrics
all_metrics.update(kris_metrics)
all_metrics.update(other_metrics)

for metric, kwargs in all_metrics.iteritems():
    # Compute weights using the default (square root) pre and post processing
    print '-computing '+metric+ ' (edge sequence:' + str(kwargs['edge_sequence']) + ')'
    v = sgraph.walk(**kwargs) #graph_walk(v0,edge_seq,AdjMat,Degs)
    df[metric] = df.id.map(sgraph.get_dict_from_vector(v))


df.to_csv('output/metrics.csv',encoding='utf-8')
print 'saved output'
