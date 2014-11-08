import json
import os
import requests
import logging
logging.basicConfig(level=logging.INFO)

MEETUP_API_KEY = 'XXX'


def main():
    meetup_group = 'Brussels-Data-Science-Community-Meetup'
    #get_meetup_members(MEETUP_API_KEY, meetup_group)
    #get_meetup_rsvps(MEETUP_API_KEY, meetup_group)
    #get_belgian_meetup_groups(MEETUP_API_KEY)
    get_belgian_meetup_group_members(MEETUP_API_KEY)
    get_belgian_meetup_group_rsvps(MEETUP_API_KEY)


def get_meetup_members(api_key, group_urlname, reload_existing=True):
    members_url = '/2/members/'
    params = dict(group_urlname=group_urlname)
    get_meetup_data(api_key, members_url, params, 'output/members/members_%s.json' % group_urlname,
                    reload_existing=reload_existing)


def get_meetup_rsvps(api_key, group_urlname, reload_existing=True):
    rsvps_url = "/2/rsvps/"
    events_url = "/2/events/"
    rsvps = []
    outfile = 'output/events/events_%s.json' % group_urlname
    events = get_meetup_data(api_key, events_url, params=dict(group_urlname=group_urlname, status='past,upcoming'),
                             outfile=outfile, reload_existing=reload_existing)

    #don't reload all group rsvps again if not needed
    outfile = 'output/rsvps/rsvps_%s.json' % group_urlname
    if not reload_existing and os.path.isfile(outfile):
        return

    for event in events:
        params = dict(event_id=event['id'])
        rsvps += get_meetup_data(api_key, rsvps_url, params, reload_existing=reload_existing)

    with open(outfile, 'w') as f:
            json.dump(rsvps, f)


def get_belgian_meetup_groups(api_key):
    params = dict(country='BE', city='Brussels')
    results = get_meetup_data(api_key, '/2/groups/', params, 'output/belgian_groups.json')

def get_belgian_meetup_group_members(api_key):
    with open('output/belgian_groups.json', 'r') as f:
        groups = json.load(f)
        for group in groups:
            get_meetup_members(MEETUP_API_KEY, group['urlname'], reload_existing=False)

def get_belgian_meetup_group_rsvps(api_key):
    with open('output/belgian_groups.json', 'r') as f:
        groups = json.load(f)
        for group in groups:
            get_meetup_rsvps(MEETUP_API_KEY, group['urlname'], reload_existing=False)


def get_meetup_data(api_key, endpoint, params, outfile='', reload_existing=True):

    if not reload_existing and outfile != '' and os.path.isfile(outfile):
        with open(outfile, 'r') as f:
            return json.load(f)

    offset = 0
    url = 'https://api.meetup.com' + endpoint
    all_results = []
    params['key'] = api_key
    more = True
    while more:
        params['offset'] = offset
        logging.info('GET %s with params %s' %(url, str(params)))
        try:
            response = requests.get(url, params=params).json()
            all_results += response['results']
            more = response['meta']['next'] != ''
            offset += 1
        except:
            logging.error("exception in %s", str(response))
            more = False

    if outfile != '':
        with open(outfile, 'w') as f:
            json.dump(all_results, f)

    return all_results


if __name__ == "__main__":
    main()