import requests
import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import locale
import tweepy
from dotenv import load_dotenv
import os


def spocitej_r(zdrojDat, datum):
    '''
    :param zdrojDat: slovnik obsahujici data z mzcr
    :param datum: datum, ke kterému se má spočítat reprodukční číslo r
    :return: číslo r
    '''

    # připrav datumy, z kterých se bude vypočítávat reprodukční číslo
    datumyCitatel = [(datum - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, 8)]
    datumyJmenovatel = [(datum - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(6, 13)]

    # vypočítej reprodukční číslo
    citatel = sum(
        [x['prirustkovy_pocet_nakazenych'] for x in zdrojDat['data'] if x['datum'] in datumyCitatel]
    )
    jmenovatel = sum(
        [x['prirustkovy_pocet_nakazenych'] for x in zdrojDat['data'] if x['datum'] in datumyJmenovatel]
    )
    reprodukcniCislo = citatel / jmenovatel
    return reprodukcniCislo

if __name__ == '__main__':
    # nastav místní formátování času na česko
    locale.setlocale(locale.LC_TIME, 'cs_CZ.UTF-8')
    # stáhni data z ministerstva
    url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakaza.json'
    res = requests.get(url)
    data = res.json()
    # připrav datumy, z kterých se bude vypočítávat reprodukční číslo
    dnes = datetime.datetime.now()
    reprodukcniCislo = spocitej_r(data, dnes)

    # vytvoř seznam cisel R za posledních třicet dnů
    tricetR = list(zip([spocitej_r(data, dnes - datetime.timedelta(days=x)) for x in range(1,31)],
    [dnes - datetime.timedelta(days=x) for x in range(1, 31)]))

    # vytvoř graf vývoje čísla R
    fig, ax  = plt.subplots()
    ax.plot([x[1] for x in tricetR], [x[0] for x in tricetR])
    formatter = mdates.DateFormatter('%b %d')
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis='x', rotation=45)
    ax.set_xlabel('Datum')
    ax.set_ylabel('Reprodukční číslo')
    ax.set_ylim(0, 3)
    ax.set_title('Vývoj reprodukčního čísla za posledních 30 dní')
    fig.savefig('trend.png')


    # přihlaš se na Twitter
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
    api.update_with_media('trend.png',
                          f'Dnes je {dnes.strftime("%d.%m.%Y")} a reprodukční číslo je {reprodukcniCislo:.2f}'
                          )
    print(f'{reprodukcniCislo:.2f}')