import json
import logging
from networkx.readwrite import json_graph
import networkx as nx
import codecs
logging.basicConfig(level=logging.WARN)


def add_potential_edge(graph, left, right, bond, ratio=0.125):
    left_set = set(left[bond])
    right_set = set(right[bond])
    intersection= len(left_set.intersection(right_set))
    union = len(left_set.union(right_set))
    if intersection == 0 or union == 0:
        return
    current_ratio = float(intersection)/float(union)
    if current_ratio > ratio:
        graph.add_edge(left['id'], right['id'], weight=current_ratio*100)
        logging.info('added edge between %s and %s' % (left['id'], right['id']))


def build_meetups_graph(groups):
    graph = nx.Graph()
    members_graph = nx.Graph()
    for group in groups:
        category_name = ''
        if 'category' in group:
            category_name = group['category']['name']
        members_graph.add_node(group['id'], name=group['name'], group=category_name, members=group['members'])
        if len(group['topic_keys']) > 0:
            graph.add_node(group['id'], name=group['name'], group=category_name, members=group['members'])
    for left in groups:
        for right in groups:
            #to make sure we add edges only once
            if left['id'] >= right['id']:
                continue
            add_potential_edge(graph, left, right, 'topic_keys', ratio=0.1)
            add_potential_edge(members_graph, left, right, 'member_keys', ratio=0.05)
    logging.info('graph built')
    d = json_graph.node_link_data(graph) # node-link format to serialize
    json.dump(d, open('html/force.json', 'w'))
    d = json_graph.node_link_data(members_graph) # node-link format to serialize
    json.dump(d, open('html/members_force.json', 'w'))


def build_group_graph(group, members, topics):
    graph = nx.Graph()
    graph.add_node(group['id'], name=group['name'], group='groups', size=group['members'])

    for topic in group['topics']:
        graph.add_node(topic['id'], name=topic['name'], group='topics', size=10)
        graph.add_edge(topic['id'], group['id'], weight=100)
        for next_topic in group['topics']:
            if topic['id'] < next_topic['id']:
                graph.add_edge(topic['id'], next_topic['id'], weight=100)

    for member_key in group['member_keys']:
        member = members[str(member_key)]
        graph.add_node(member['id'], name=member['name'], group='members', size=1)
        topic_keys = set([topic['id'] for topic in member['topics']])

        member_connected=False
        for topic in group['topics']:
            if topic['id'] in topic_keys:
                graph.add_edge(topic['id'], member['id'], weight=100)
                member_connected = True

        if not member_connected:
            graph.add_edge(group['id'], member['id'], weight=100)

    for topic in group['topics']:
        id = topic['id']
        #neighbours = len(nx.all_neighbors(graph, id))-1
        neighbours = len(graph.edge[id])
        graph.node[id]['size'] = neighbours

    logging.info('graph built')
    d = json_graph.node_link_data(graph) # node-link format to serialize
    json.dump(d, open('html/group.json', 'w'))


def find_group(groups, urlname):
    for group in groups:
        if group['urlname'] == urlname:
            return group
    return None


def main():
    topics = json.load(codecs.open('output/topics.json', 'r', encoding='utf-8'))
    members = json.load(codecs.open('output/members.json', 'r', encoding='utf-8'))
    groups = json.load(codecs.open('output/groups.json', 'r', encoding='utf-8'))

    build_meetups_graph(groups)
    group = find_group(groups,'Brussels-Data-Science-Community-Meetup')
    build_group_graph(group, members, topics)


if __name__ == "__main__":
    main()