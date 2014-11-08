import json
from twython import Twython
import requests
import logging
logging.basicConfig(level=logging.INFO)

TWITTER_APP_KEY = 'XXX'
TWITTER_ACCESS_TOKEN = 'XXX'



def main():
    twitter = get_twitter_handle()
    get_followers(twitter, "DataScienceBe")


def get_followers(twitter, screen_name):
    cursor = -1
    all_followers = []
    while cursor != 0:
        followers = twitter.get_followers_list(screen_name=screen_name, count=200, cursor=cursor)
        all_followers += followers['users']
        cursor = followers['next_cursor']

    for follower in all_followers:
        print "User %s is following %s" % (follower['screen_name'], screen_name)
    with open('output/followers.json', 'w') as outfile:
        json.dump(all_followers, outfile)


def get_twitter_handle():

    twitter = Twython(TWITTER_APP_KEY, access_token=TWITTER_ACCESS_TOKEN)
    return twitter


if __name__ == "__main__":
    main()