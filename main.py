import requests
import datetime
import tweepy
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    # stáhni data z ministerstva
    url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakaza.json'
    res = requests.get(url)
    data = res.json()
    # připrav datumy, z kterých se bude vypočítávat reprodukční číslo
    dnes = datetime.datetime.now()
    datumyCitatel = [(dnes - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, 8)]
    datumyJmenovatel = [(dnes - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(6, 13)]
    # vypočítej reprodukční číslo
    citatel = sum(
        [x['prirustkovy_pocet_nakazenych'] for x in data['data'] if x['datum'] in datumyCitatel]
    )
    jmenovatel = sum(
        [x['prirustkovy_pocet_nakazenych'] for x in data['data'] if x['datum'] in datumyJmenovatel]
    )
    reprodukcniCislo = citatel/jmenovatel
    # TODO přihlaš se na Twitter
    load_dotenv()
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    # tweetni reprodukční číslo
    api.update_status(f'Dnes je {dnes.strftime("%d.%m.%Y")} a reprodukční číslo je {reprodukcniCislo:.2f}')
