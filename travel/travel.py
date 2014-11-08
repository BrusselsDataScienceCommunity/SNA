import json
import pandas

def main():
    with open('output/members_Brussels-Data-Science-Community-Meetup.json', 'r') as f:
        members = json.load(f)
    with open('output/rsvps_Brussels-Data-Science-Community-Meetup.json', 'r') as f:
        rsvps = json.load(f)
    cities = {}

    member_dict = {}
    for member in members:
        member_dict[member['id']] = member
    member_dict

    for member in members:
        city = member['city']
        if not city in cities:
            cities[city]={}
            cities[city]['members']=1
            cities[city]['rsvps'] =0
        else:
            cities[city]['members']+=1

    for rsvp in rsvps:
        member_id= rsvp['member']['member_id']
        city = member_dict[member_id]['city']
        if rsvp['response'] != 'yes':
            continue
        if not city in cities:
            cities[city]={}
            cities[city]['members'] = 0
            cities[city]['rsvps'] = 1
        else:
            cities[city]['rsvps']+=1

    with open('output/distance.csv', 'w') as f:
        for key,value in cities.iteritems():
            f.write("%s,%d,%d\n" %(key.encode('utf8'), value['members'], value['rsvps']))




if __name__ == "__main__":
    main()