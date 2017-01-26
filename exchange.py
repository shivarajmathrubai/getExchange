from flask import Flask, make_response
from flask import request
from flask import json
import requests
import logging
import redis

import random

logging.basicConfig(filename='exchange-webhook.log',level=logging.DEBUG, format='%(asctime)s %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
url = "https://www.google.com/finance/converter"
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("### Webhook called ###")
    req = request.get_json(silent=True, force=True)
    logreq(req)
    intent = getIntent(req)
    if intent == "getExhangeRate":
        cur =(req['result']['parameters']['currency-name'], 'INR', '1')
        k = (getMultiCur(cur),'INR')
    elif intent == "multiCurrency":
        cur = (req['result']['parameters']['input-currency'], req['result']['parameters']['output-currency'], '1')
        k = (getMultiCur(cur),req['result']['parameters']['output-currency'])
    elif intent == "withamount":
        cur = (req['result']['parameters']['unit-currency']['currency'], req['result']['parameters']['currency-name'], req['result']['parameters']['unit-currency']['amount'])
        k = (getMultiCur(cur),req['result']['parameters']['currency-name'])
    else:
        k = ("Oppppsss.... ","Something really Bad happened.. Try that agian ?")
    return formresponse(k)

def logreq(req):
    try:
        logger.info("### Initiating REDIS Connection ####")
        r = redis.StrictRedis(host='localhost', port=6379, db=1)
        r.ping()
    except Exception:
        logging.exception("### Could not connect to REDIS ###")
        pass

    if r.exists("COUNTER"):
        pass
    else:
        r.set("COUNTER",0)
    unq = r.incr("COUNTER",1)
    r.hset("REQUEST",unq,req)
    logger.debug("### Counter from redis is {} ####".format(r.get("COUNTER")))
    logger.info("### Request registered in REDIS###")

def getIntent(req):
    logger.info("### Checking Intent Name ###")
    try:
        intent = req['result']['metadata']['intentName']
        if intent == "getExhangeRate":
            return intent
        elif intent == "multiCurrency":
            return intent
        elif intent == "withamount":
            return intent
    except(TypeError,ValueError,Exception):
        logger.error("### Input was not in the right format ###")

def getMultiCur(intup):
    #print(intup)
    incur,outcur,amt = intup #tuple
    logger.info("### Multi-Currency Flow triggered ###")
    payload = {'a':amt, 'from':incur, 'to':outcur}
    fullhtml = requests.get(url, params=payload)
    a = fullhtml.text
    b = a.split()[-14]
    v = b.split('>')[1]
    return v

def formresponse(k):
    val,curr = k
    responses = ["Okay, it's {} {}".format(val,curr),
                 "The current rate is {} {}".format(val,curr),
                 "The exchange rate is {} {}".format(val,curr),
                 "it's {} {}".format(val,curr)]
    d = random.choice(responses)
    data = {}
    data['speech'] = d
    data['displayText'] = d
    data['data'] = ''
    data['contextOut'] = ''
    data['source'] = 'TPYBOT'
    jsondata = json.dumps(data)
    final = make_response(jsondata)
    final.headers['Content-Type'] = "application/json"
    return final

if __name__ == '__main__':
    app.run(debug=True)
