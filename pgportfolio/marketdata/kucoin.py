import json
import time
import sys
import base64
import hmac
import hashlib
import requests
from datetime import datetime

# minute = 60
# hour = minute * 60
# day = hour * 24
# week = day * 7
# month = day * 30
# year = day * 365


class KuCoin:
    def __init__(self, secrets='../../../secrets.txt'):
        self.API_KEY, self.API_SECRET = self.__setup_key(secrets)
        self.url = 'https://api.kucoin.com'
        self.session = requests.session()

    def __setup_key(self, secrets):
        with open(secrets) as f:
            key = str(f.readline().split(':')[1]).replace('\n', '')
            secret = str(f.readline().split(':')[1]).replace('\n', '')
        return key, secret

    def market_volume(self, data={}):
        endpoint = '/v1/open/tick'
        headers = self.generate_header(endpoint, data)

        self.session.headers.update(headers)
        uri = '{}{}'.format(self.url, endpoint)

        response = getattr(self.session, 'get')(uri)
        return response.json()

    def generate_header(self, endpoint, data):
        nonce = int(time.time() * 1000)
        return {
            'Accept': 'application/json',
            'User-Agent': 'python-kucoin',
            'HTTP_ACCEPT_LANGUAGE': 'en-US',
            'Accept-Language': 'en-US',
            'KC-API-KEY': self.API_KEY,
            'KC-API-NONCE': str(nonce),
            'KC-API-SIGNATURE': self.generate_signature(endpoint, data, nonce),
        }

    def generate_signature(self, endpoint, data, nonce):
        """Generate the call signature
        :param data:
        :param nonce:
        :return: signature string
        """
        query_string = self.generate_params(data)
        sig_str = ("{}/{}/{}".format(endpoint, nonce,
                                     query_string)).encode('utf-8')
        m = hmac.new(
            self.API_SECRET.encode('utf-8'), base64.b64encode(sig_str),
            hashlib.sha256)
        return m.hexdigest()

    def generate_params(self, data):
        strs = []
        for key in sorted(data):
            strs.append('{}={}'.format(key, data[key]))
        return '&'.join(strs)