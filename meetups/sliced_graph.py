import logging
import networkx as nx
import numpy as np
import math
import cPickle as pickle
import os
import scipy.stats
from collections import defaultdict

logging.basicConfig(level=logging.WARN)

### Auxiliary functions




# General purpose function for slicing a graph
# G : graph to be sliced
# ntypes, etypes : (string or list of strings) node/edge types to slice 
# only keep nodes and edges before or on the given date.
def graph_slice(G,ntypes=[],etypes=[],date=None,inplace=False,removeedges=False):
    if isinstance(ntypes, basestring):
        ntypes = [ntypes]
    if isinstance(etypes, basestring):
        etypes = [etypes]

    if inplace:
        H = G
    else:
        H = G.copy()
    
    #remove_nodes = []
        
    if len(ntypes)>0:
        remove_nodes = [n[0] for n in H.nodes(data=True) if ('ntype' not in n[1]) or n[1]['ntype'] not in ntypes]
        H.remove_nodes_from(remove_nodes)
    if date:
        #keep_nodes = [n for n in keep_nodes if ('date' not in n[1]) or n[1]['date']<=date]
        remove_nodes = [n[0] for n in H.nodes(data=True) if ('date' in n[1]) and n[1]['date']>date]
        H.remove_nodes_from(remove_nodes)
            #s_from([n for n in G.nodes(data=True) if n not in keep_nodes])

    #keep_edges = H.edges(data=True)
    if len(etypes)>0:
        remove_edges = [e for e in H.edges(data=True) if e[2]['etype'] not in etypes]
        H.remove_edges_from(remove_edges)
    if date:
        remove_edges = [e for e in H.edges(data=True) if 'date' in e[2] and e[2]['date']>date]
        H.remove_edges_from(remove_edges)
    return H

procs = {
    'L2' : lambda v,Degs : v / np.sqrt(Degs),
    'L1' : lambda v,Degs : v / Degs,
    'noprocess' : lambda v,Degs : v}
norms = {
    'one' : lambda v : 1,
    'L1' : lambda v : sum(v),
    'L2' : np.linalg.norm,
    'gmean' : lambda v : scipy.stats.gmean(v[np.nonzero(v)])}

class Sliced_graph:
    
    def __init__(self,**kwargs):
        
        self.v0 = None if 'v0' not in kwargs else kwargs['v0']
        self.AdjMat = None if 'AdjMat' not in kwargs else kwargs['AdjMat']
        self.Degs = None if 'Degs' not in kwargs else kwargs['Degs']
        self.OrderedNodes = None if 'OrderedNodes' not in kwargs else kwargs['OrderedNodes']

    def walk(self,edge_sequence,**kwargs):
        preprocess= procs['noprocess'] if 'preprocess' not in kwargs else kwargs['preprocess']
        postprocess=procs['noprocess'] if 'postprocess' not in kwargs else kwargs['postprocess']
        norm = norms['one'] if 'norm' not in kwargs else kwargs['norm']
        if not isinstance(preprocess,list):
            preprocess = [preprocess]*len(edge_sequence)
        if not isinstance(postprocess,list):
            postprocess = [postprocess]*len(edge_sequence)

        v = self.v0
        for prepr, etype, postpr in zip(preprocess, edge_sequence, postprocess):
            v = prepr(v,self.Degs[etype])
            v = self.AdjMat[etype].dot(v)
            v = postpr(v,self.Degs[etype])
        n = norm(v)
        if n !=0:
            return v / n
        else:
            return v
    
    def node_to_vector(self,node):
        v = np.zeros((len(self.OrderedNodes),1))
        v[self.NodeIndex[node],0] = 1
        return v

    def nodes_to_matrix(self,nodelist):
        mat = np.zeros((len(self.OrderedNodes),len(nodelist)))
        for idx,node in enumerate(nodelist):
            mat[self.NodeIndex[node],idx]=1
        return mat


    def get_dict_from_vector(self,v):
        col={}
        v = v.flatten()
        for idx in range(len(v)):
            col[self.OrderedNodes[idx][1]] = v[idx]
        return col

    # Compute graph slices in matrix form + auxiliary data
    def compute_slice_matrices(self,G):
        #Create node and edge layers
        node_layer = defaultdict(list)
        for n in G.nodes():
            node_layer[n[0]].append(n)

        edge_layer = defaultdict(list)
        for e in G.edges(data=True):
            edge_layer[e[2]['etype']].append(e)

        ALLNTYPES = [ntype for ntype in node_layer] 
        ALLETYPES = [etype for etype in edge_layer]

        #### Transform everything into linear algebra...

        self.OrderedNodes=[]
        for ntype in ALLNTYPES:
            self.OrderedNodes = self.OrderedNodes + node_layer[ntype]
        self.NodeIndex = {}
        for idx,n in enumerate(self.OrderedNodes):
            self.NodeIndex[n]=idx

        #Construct Adjacency Matrices for various slices (single edge type)
        self.AdjMat = {}
        self.Degs = {} # Degre
        #Invdegs = {}
        for etype in ALLETYPES:
            print '--computing slice for edge type "'+etype+'"'
            H = graph_slice(G,etypes=etype)
            self.AdjMat[etype] = nx.to_scipy_sparse_matrix(H,self.OrderedNodes,format='csr')
            self.Degs[etype] = np.array([[max(1,float(H.degree(n)))] for n in self.OrderedNodes])
            #Invdegs[etype] = np.reciprocal(Degs[etype])

    def to_pickle(self,picklefile):
        #Pickle the results to file
        #first, make sure the dir exists
        d = os.path.dirname(picklefile)
        if not os.path.exists(d):
            os.makedirs(d)
        with open(picklefile,'w') as f:
            pickle.dump(self,f)

def read_pickle(picklefile):
    with open(picklefile,'r') as f:
        return pickle.load(f)


  