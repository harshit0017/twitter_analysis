import asyncio
import warnings
import contextlib
from urllib3.exceptions import InsecureRequestWarning
from twikit import Client, TooManyRequests
import csv
from datetime import datetime
from configparser import ConfigParser
from random import randint
import requests

# Constants
MINIMUM_TWEETS = 10
QUERY = '@airindia lang:en until:2025-02-18 since:2025-02-01'

# Context manager to disable SSL verification
old_merge_environment_settings = requests.Session.merge_environment_settings

@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        opened_adapters.add(self.get_adapter(url))
        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False
        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings
        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

async def get_tweets(client, tweets):
    """Fetch tweets asynchronously."""
    if tweets is None:
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets

async def main():
    """Main function to fetch and process tweets."""
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    with open('tweets3.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes', 'Media URLs'])

    client = Client(language='en-US')

    with no_ssl_verification():
        client.load_cookies('twitter_fetch/creds/cookies.json')

        tweet_count = 0
        tweets = None

        while tweet_count < MINIMUM_TWEETS:
            try:
                tweets = await get_tweets(client, tweets)
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                wait_time = (rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
                continue

            if not tweets:
                print(f'{datetime.now()} - No more tweets found')
                break

            for tweet in tweets:
                tweet_count += 1

                media_urls = [media._data["media_url_https"] for media in tweet.media] if tweet.media else []
                media_urls_str = ", ".join(media_urls) if media_urls else "No Media"

                tweet_data = [
                    tweet_count,
                    tweet.user.name,
                    tweet.text,
                    tweet.created_at,
                    tweet.retweet_count,
                    tweet.favorite_count,
                    media_urls_str
                ]

                with open('tweets3.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(tweet_data)

            print(f'{datetime.now()} - Got {tweet_count} tweets')

    print(f'{datetime.now()} - Done! Got {tweet_count} tweets')

asyncio.run(main())
