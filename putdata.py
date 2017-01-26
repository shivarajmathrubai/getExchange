import redis
import logging
import requests

logging.basicConfig(filename='exchange-putdata.log',level=logging.DEBUG, format='%(asctime)s %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("### Initiating REDIS Connection ####")
    r = redis.StrictRedis(host='localhost', port=6379, db=1)
    r.ping()
except Exception:
    logging.exception("### Could not connect to REDIS ###")
    raise

curshort = []
countries = []
currencies = []
url = "http://apilayer.net/api/live?access_key=9a5e786ef86fdd4345be4bf241fcda31&source=USD&format=1"

def putcurrency():
    logger.info( "### Starting putcurrency ###")
    with open("currency-codes.txt", mode='r', encoding='utf-8') as incurrency:
        for line in incurrency:
            a = line.rsplit(",")
            logger.debug("## Writing each currency to Redis here ##")
            r.hset("curname", a[1].upper(), a[2].upper().replace('\n','')) #curname key will hold currency name and currenchy short code
            r.hset("couname", a[0].upper(), a[2].upper().replace('\n','')) #couname key will hold country to currency short code mapping
            curshort.append(a[2].upper().replace('\n',''))
            countries.append(a[0].upper())
            currencies.append(a[1].upper())
            #print(a)
        r.hset("master", "currencylist", currencies)  #Master currency name list
        r.hset("master", "countrieslist", countries)   #Master countries list
        r.hset("master", "currencyshortlist", curshort) #Master currency short code list
    logger.info("### End of putcurrency ##")


def getrates():
    logger.info("### Getting the rates from apilayer ###")
    rates= requests.get(url, allow_redirects=False)
    #print(rates.status_code)
    if rates.status_code == 200:
        jrates = rates.json()
        #print(jrates['code'])
        if jrates['success'] is False :
            logger.error("### Got HTTP 200 from APIlayer but didn't get any data ##")
            logger.error(jrates)
        else:
            val = jrates['quotes']
            for i in val:
                r.hset("rates",i[3:],val[i])
            logger.info("## APIlayer sucess ##")
    elif rates.status_code != 200:
        logger.error("### Something went wrong when accessing apilayer api - Got non-200 http response !###")

def main():
    logger.info("### Starting putdata ###")
    #putcurrency()
    getrates()
    logger.info("### End of putdata ###")

if __name__ == '__main__': main()












