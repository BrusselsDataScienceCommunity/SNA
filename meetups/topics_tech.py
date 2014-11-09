import json
import logging
from networkx.readwrite import json_graph
import networkx as nx
logging.basicConfig(level=logging.WARN)


def add_potential_edge(graph, left, right, bond, ratio=0.125):
    intersection= len(left[bond].intersection(right[bond]))
    union = len(left[bond].union(right[bond]))
    if intersection == 0 or union == 0:
        return
    current_ratio = float(intersection)/float(union)
    if current_ratio > ratio:
        graph.add_edge(left['id'], right['id'], weight=current_ratio*100)
        logging.info('added edge between %s and %s' % (left['id'], right['id']))


def extract_topics(groups):
    topics = {}
    for group in groups:
        group['topic_keys'] = set()
        for topic in group['topics']:
            key = topic['id']
            topics[key] = topic
            group['topic_keys'].add(key)
    return topics


def extract_members(groups):
    all_members = {}
    for group in groups:
        group['member_keys'] = set()
        members = json.load(open('../crawlers/output/members/members_%s.json' % group['urlname'], 'r'))
        for member in members:
            key = member['id']
            if not key in all_members:
                #bio is different per meetup group. Ignoring that.
                all_members[key] = member
            group['member_keys'].add(key)
    return all_members

def remove_leafs(G,recursive=True):
    foundleaf=True
    while foundleaf:
        foundleaf=False
        for v in G.nodes():
            if G.degree(v)<2:
                foundleaf=recursive
                G.remove_node(v)

def get_main_cc(G):
    ccs = list(nx.connected_components(G))
    maxlen=0
    for cc in ccs:
        if len(cc) > maxlen:
            maxlen = len(cc)
            maxcc=cc
    return G.subgraph(maxcc).copy()


def main():

    #meetupfrom = 'belgian_groups.json'
    meetupfrom = 'groups_be_tech.json'
    with open('../crawlers/output/'+meetupfrom, 'r') as f:
        groups = json.load(f)

    #only look at groups with at least 10 people
    #groups = [group for group in groups if group['members'] >= 10]
    topics = extract_topics(groups)
    members = extract_members(groups)

    full_graph = nx.Graph()
    common_topics_graph = nx.Graph() #Node=group Edge=common topic
    common_members_graph = nx.Graph() #Node=group Edge=common members
    topics_and_groups_graph = nx.Graph() #Node=group or topic Edge=is a topic of (undirected)
    topics_graph = nx.Graph() #Node=topic Edge=common group
    for key in topics:
        topics_and_groups_graph.add_node(key, name=topics[key]['name'][:0],fullname=topics[key]['name'], group='', type='topic')
    for group in groups:
        category_name = ''
        if 'category' in group:
            category_name = group['category']['name']
        common_members_graph.add_node(group['id'], name=group['name'][:20],fullname=group['name'], group=category_name, members=group['members'])
        if len(group['topic_keys']) > 0:
            common_topics_graph.add_node(group['id'], name=group['name'][:20],fullname=group['name'], group=category_name, members=group['members'])
            topics_and_groups_graph.add_node(group['id'], name=group['name'][:15],fullname=group['name'], group=category_name, members=group['members'], type='group')
            for key in group['topic_keys']:
                topics_and_groups_graph.add_edge(group['id'],key)
    for key in topics:
        topics_and_groups_graph.node[key]['members']=10*(topics_and_groups_graph.degree(key)-1)
    remove_leafs(topics_and_groups_graph)

    #Get Brussels Data Science Meetup
    for group in groups:
        if group['name']=='Brussels Data Science Meetup':
            BDS = group

    for v in topics_and_groups_graph.nodes():
        if topics_and_groups_graph.node[v]['type']=='topic':
            gp=''
            if v in BDS['topic_keys']:
                gp='inBDS'
            topics_graph.add_node(v, name=topics[v]['name'],fullname=topics[v]['name'], group=gp,members=10*(topics_and_groups_graph.degree(v)+1))
    for v in topics_graph.nodes():
        for w in topics_graph.nodes():
            if v < w:
                nv = set(topics_and_groups_graph[v])
                nw = set(topics_and_groups_graph[w])
                u = len(nv.union(nw))
                if u>0:
                    ratio = float(len(nv.intersection(nw)))/float(u)
                    if ratio > .25:
                        topics_graph.add_edge(v,w,weight=ratio*10)

    for left in groups:
        for right in groups:
            #to make sure we add edges only once
            if left['id'] >= right['id']:
                continue
            add_potential_edge(common_topics_graph, left, right, 'topic_keys')
            add_potential_edge(common_members_graph, left, right, 'member_keys', ratio=0.05)

    topics_graph = get_main_cc(topics_graph)
    common_topics_graph = get_main_cc(common_topics_graph)
    common_members_graph = get_main_cc(common_members_graph)

    logging.info('graph built')


    d = json_graph.node_link_data(common_topics_graph) # node-link format to serialize
    json.dump(d, open('html/common_topics_graph_tech.json','w'))
    d = json_graph.node_link_data(common_members_graph) # node-link format to serialize
    json.dump(d, open('html/common_members_graph_tech.json','w'))
    d = json_graph.node_link_data(topics_and_groups_graph) # node-link format to serialize
    json.dump(d, open('html/topics_and_groups_graph_tech.json','w'))
    d = json_graph.node_link_data(topics_graph) # node-link format to serialize
    json.dump(d, open('html/topics_graph_tech.json','w'))
    print('Wrote node-link JSON data files as html/*.json')


if __name__ == "__main__":
    main()