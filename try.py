import asyncio
from twikit import Client, TooManyRequests
import csv
from datetime import datetime
from configparser import ConfigParser
from random import randint

# Constants
MINIMUM_TWEETS = 10
QUERY = '@airindia lang:en until:2025-02-17 since:2025-02-01'

async def get_tweets(client, tweets):
    """Fetch tweets asynchronously."""
    if tweets is None:
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()  # Awaiting the coroutine
    return tweets

async def main():
    """Main function to fetch and process tweets."""
    # Read login credentials
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    # Create CSV file
    with open('tweets3.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes', 'Media URLs'])

    # Authenticate to X.com
    client = Client(language='en-US')
    client.load_cookies('cookies.json')

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
            image_urls = []

            # Extract image URLs
            if tweet.media:
                print(f"Media: {tweet.media}")
                media_urls = [media._data["media_url_https"] for media in tweet.media]
            else:
                media_urls = []  # Ensure media_urls is always defined

            media_urls_str = ", ".join(media_urls) if media_urls else "No Media"

            tweet_data = [
                tweet_count,
                tweet.user.name,
                tweet.text,
                tweet.created_at,
                tweet.retweet_count,
                tweet.favorite_count,
                media_urls_str  # Add image URLs here
            ]

            with open('tweets3.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

        print(f'{datetime.now()} - Got {tweet_count} tweets')

    print(f'{datetime.now()} - Done! Got {tweet_count} tweets')

# Run the async function properly
asyncio.run(main())
