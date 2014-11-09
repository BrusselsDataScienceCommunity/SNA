import json
import logging
import csv
import networkx as nx
import codecs
from enum import Enum
logging.basicConfig(level=logging.INFO)


class Type(Enum):
    Groups = 1
    Members = 2
    Topics = 3
    Events = 4
    Membership = 5
    Interest = 6
    Attendance = 7


def link_members(graph, group, members):
    for member_key in group['member_keys']:
        member = members[str(member_key)]
        if member_key not in graph:
            graph.add_node(member_key, name=member['name'], type=Type.Members)
        graph.add_edge(group['id'], member_key, type=Type.Membership)


def link_topics(graph, group, topics):
    for topic_key in group['topic_keys']:
        topic = topics[str(topic_key)]
        if topic_key not in graph:
            graph.add_node(topic_key, name=topic['name'], type=Type.Topics)
            logging.info('added topic %d: %s as group interest' %(topic_key, topic['name']))
        graph.add_edge(group['id'], topic_key, type=Type.Interest)


def link_members_to_topics(graph, members, topics):
    for key, value in topics.iteritems():
        key = int(key)
        if key not in graph:
            graph.add_node(key, name=value['name'], type=Type.Topics)
            logging.info('added topic %d: %s as member interest' %(key, value['name']))
    for key, member in members.iteritems():
        for topic in member['topics']:
            graph.add_edge(member['id'], topic['id'], type=Type.Interest)


def link_members_to_events(graph, members, events):
    for key, event in events.iteritems():
        if key not in graph:
            graph.add_node(key, name=event['name'], type=Type.Events)
        for member_key in event['member_keys']:
            if str(member_key) in members:
                member = members[str(member_key)]
            else:
                logging.warn('member %d for event %s unkown in memberlist' %(member_key, event['name']))
            graph.add_edge(member['id'], event['id'], type=Type.Attendance)


def build_meetups_graph(groups, topics, members, events):
    graph = nx.Graph()
    for group in groups:
        key = group['id']
        graph.add_node(key, name=group['name'], type=Type.Groups, members=group['members'])
        link_members(graph, group,members)
        link_topics(graph, group, topics)
    link_members_to_topics(graph, members, topics)
    link_members_to_events(graph, members, events)
    nx.freeze(graph)

    logging.info('graph built')
    return graph


def calculate_connectedness_member(graph, center, candidate):
    #calculate all direct connections with our meetup groups
    #direct meaning: you're a member of the same meetup group as a member of us
    members = get_all_members(graph, center)
    candidate_groups = set(get_all_groups(graph, candidate))
    connectedness = 0
    for member in members:
        groups = set(get_all_groups(graph, member))
        connectedness += len(groups.intersection(candidate_groups))
    return connectedness


def initialize_candiate(members_dict, key):
    return dict(info=members_dict[str(key)], connectedness=0, activity=0, interests=0)


def calculate_interests_member(graph, center, candidate):
    center_interests = set(get_all_topics(graph, center))
    member_interests = set(get_all_topics(graph, candidate))
    interests = len(center_interests.intersection(member_interests))/float(len(center_interests.union(member_interests)))
    return interests


def calculate_metrics(candidates, graph, center, members_dict):
    # get all members of our meetup group
    members = get_all_members(graph, center)

    count = 0
    for key, member in members_dict.iteritems():
        key = int(key)
        #ignore current members
        if key in members:
            continue
        interests = calculate_interests_member(graph, center, key)
        activity = calculate_activity_member(graph, members, key)
        connectedness = calculate_connectedness_member(graph, center, key)
        count += 1
        #don't add potential members if there is no interests shared
        if interests == 0:
            continue
        if key not in candidates:
            candidates[key] = initialize_candiate(members_dict, key)
        candidates[key]['interests'] = interests
        candidates[key]['activity'] = activity
        candidates[key]['connectedness'] = connectedness
        logging.info('%d/%d set member metrics of %s to %f - %f - %f',
                     count, len(members_dict), candidates[key]['info']['name'], interests, activity, connectedness)


def calculate_activity_member(graph, members, candidate):
    activity = 0
    candidate_activity = set(get_all_events(graph, candidate))
    events_attended = len(candidate_activity)
    if events_attended == 0:
        return 0
    for member in members:
        member_activity = set(graph.neighbors(member))
        #add all events which were attented by both this member and the candidate
        activity += len(member_activity.intersection(candidate_activity))

    return float(activity)


def build_new_member_list(group, graph, members_dict):
    '''
        collect 3 metrics to identify good candidates:
        1. Activity: should be active in the meetup groups
        2. Connectedness: Should be closely connected to our current members
        3. Interests: should share many of the interests of the group
    '''
    candidates = {}
    center = group['id']

    calculate_metrics(candidates, graph, center, members_dict)

    return candidates


def get_all_groups(graph, member_keys):
    return get_all_neighbours(graph, member_keys, Type.Membership)


def get_all_members(graph, group_keys):
    return get_all_neighbours(graph, group_keys, Type.Membership)


def get_all_topics(graph, keys):
    return get_all_neighbours(graph, keys, Type.Interest)


def get_all_events(graph, member_keys):
    return get_all_neighbours(graph, member_keys, Type.Attendance)




def get_all_neighbours(graph, keys, edgetype):
        return [edge[1] for edge in graph.edges_iter(keys, data=True) if edge[2]['type']==edgetype]


def find_group(groups, urlname):
    for group in groups:
        if group['urlname'] == urlname:
            return group
    return None


def save(new_members, filename):
    sorted_members = sorted(new_members.values(), key=lambda m: m['activity'], reverse = True)
    with open(filename, 'w', ) as csvfile:
        w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        w.writerow(['id', 'name', 'connectedness', 'interests', 'activity', 'url', 'thumb', 'photo'])
        for member in sorted_members:
            logging.info('saving %s', str(member))
            thumb = None
            photo = None
            if 'photo' in member['info']:
                thumb = member['info']['photo']['thumb_link']
                photo = member['info']['photo']['photo_link']
            w.writerow([member['info']['id'], member['info']['name'].encode('utf8'),
                        member['connectedness'], member['interests'],member['activity'],
                        member['info']['link'], thumb, photo])


def main():
    topics = json.load(codecs.open('output/topics.json', 'r', encoding='utf-8'))
    members = json.load(codecs.open('output/members.json', 'r', encoding='utf-8'))
    groups = json.load(codecs.open('output/groups.json', 'r', encoding='utf-8'))
    events = json.load(codecs.open('output/events.json', 'r', encoding='utf-8'))

    graph = build_meetups_graph(groups, topics, members, events)

    group = find_group(groups, 'Brussels-Data-Science-Community-Meetup')
    new_members = build_new_member_list(group, graph, members)
    save(new_members, 'output/new_members.csv')

if __name__ == "__main__":
    main()