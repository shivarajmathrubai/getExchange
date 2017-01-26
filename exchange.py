from flask import Flask, make_response
from flask import request
from flask import json
import requests
import logging

import re

logging.basicConfig(filename='exchange-webhook.log',level=logging.DEBUG, format='%(asctime)s %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
url = "https://www.google.com/finance/converter"
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("### Webhook called ###")
    req = request.get_json(silent=True, force=True)
    cur = req['result']['parameters']
    k = getINR(cur['currency-name'])
    return formresponse(k)


def getINR(cur):
    payload = {'a':'1', 'from':cur, 'to':'INR'}
    fullhtml = requests.get(url, params=payload)
    #print(fullhtml.url)
    a = fullhtml.text
    b = a.split()[-14]
    #print(b)
    v = b.split('>')[1]
    return v

def formresponse(k):
    data = {}
    data['speech'] = k
    data['displayText'] = k
    data['data'] = ''
    data['contextOut'] = ''
    data['source'] = 'getExchange'
    jsondata = json.dumps(data)
    final = make_response(jsondata)
    final.headers['Content-Type'] = "application/json"
    return final

if __name__ == '__main__':
    app.run(debug=True)
