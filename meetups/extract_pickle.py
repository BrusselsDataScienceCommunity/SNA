import json
import pickle
import logging
logging.basicConfig(level=logging.WARN)
import datetime

def extract_topics(groups):
    topics = {}
    for group in groups:
        group['topic_keys'] = [topic['id'] for topic in group['topics']]
        for topic in group['topics']:
            key = int(topic['id'])
            topics[key] = topic
    return topics


def extract_members(groups):
    all_members = {}
    for group in groups:
        group['member_keys'] = []
        group['join_date'] = []
        members = json.load(open('../crawlers/output/members/members_%s.json' % group['urlname'], 'r'))
        for member in members:
            key = int(member['id'])
            if not key in all_members:
                #bio is different per meetup group. Ignoring that.
                all_members[key] = member
            group['member_keys'].append(key)
            group['join_date'].append(datetime.datetime.fromtimestamp(member['joined']/1e3))
            
    return all_members

def extract_events(groups):
    all_events = {}
    for group in groups:
        group['event_keys'] = []
        rsvps = json.load(open('../crawlers/output/rsvps/rsvps_%s.json' % group['urlname'], 'r'))
        for rsvp in rsvps:
            if rsvp['response'] != 'yes':
                continue
            member = int(rsvp['member']['member_id'])
            key = rsvp['event']['id']
            if not key in all_events:
                all_events[key] = rsvp['event']
                all_events[key]['member_keys'] = []
            all_events[key]['member_keys'].append(member)
            group['event_keys'].append(key)
    return all_events


def main():
    with open('../crawlers/output/belgian_groups.json', 'r') as f:
        groups = json.load(f)

    #only look at groups with at least 10 people
    #groups = [group for group in groups if group['members'] >= 10]
    topics = extract_topics(groups)
    members = extract_members(groups)
    events = extract_events(groups)
    pickle.dump(topics, open('pickle/topics.pkl', 'w'))
    pickle.dump(members, open('pickle/members.pkl', 'w'))
    pickle.dump(groups, open('pickle/groups.pkl', 'w'))
    pickle.dump(events, open('pickle/events.pkl', 'w'))


if __name__ == "__main__":
    main()