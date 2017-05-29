import json
import re
from os.path import dirname, join, realpath

import tweepy
from mastodon import Mastodon

with open(join(dirname(realpath(__file__)), 'config.json')) as fobj:
    config = json.loads(fobj.read())


def twitter():
    auth = tweepy.OAuthHandler(**config['twitter_auth'])
    auth.set_access_token(**config['twitter_access_token'])

    return tweepy.API(auth)


def post_toot(text):
    mastodon = Mastodon(client_id='twitter2mastodon_client_cred.txt',
                        access_token='twitter2mastodon_user_cred.txt',
                        api_base_url=config['mastodon_api_base_url'])
    return mastodon.toot(text)


def get_timeline(since_id):
    t = twitter()
    return t.user_timeline(config['twitter_username'], since_id=since_id,
                           exclude_replies=True, include_rts=False)


def main():
    with open(join(dirname(realpath(__file__)), 'last_tweet.txt')) as fobj:
        last_tweet = fobj.read()

    for tweet in get_timeline(last_tweet):
        text = tweet.text

        for url in tweet.entities.get('urls'):
            text = text.replace(url['url'], url['expanded_url'])

        for media in tweet.entities.get('media', []):
            text = text.replace(media['url'], url['expanded_url'])

        for mention in tweet.entities.get('user_mentions'):
            screen_name = re.compile(re.escape('@' + mention['screen_name']),
                                     re.IGNORECASE)
            text = screen_name.sub(mention['screen_name'], mention['name'])

        toot = post_toot(text)

        with open('tweet2toot.csv', 'a') as fobj:
            fobj.write('{0},{1},{2}'.format(tweet.id,
                                            toot['id'],
                                            toot['url']))

        with open('last_tweet.txt', 'w') as fobj:
            fobj.write('{}'.format(tweet.id))


if __name__ == '__main__':
    main()
