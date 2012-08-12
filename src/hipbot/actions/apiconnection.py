from urllib import urlencode
import json
import requests

class APIError(Exception):
    pass

class APIConnection(object):

    def __init__(self, url, api_token=None):
        self.session = requests.session(
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.token = api_token
        self.url = url 

    def request(self, method, path=None, params=None, body=None):

        if path:
            if not path.startswith('/'):
                path = '/' + path
            url = self.url + path
        else:
            url = self.url

        params = params or {}
        params.update({'format': 'json'})
        if self.token:
            params.update({'auth_token': self.token})
        
        url += '?' + urlencode(params)
        response = self.session.request(method, url, data=body)
        if response.status_code != 200:
            raise APIError(response.text)
        return response.text

    def get(self, path, params=None):
        return json.loads(self.request('GET', path, params))

    def post(self, path, params=None, body=None):
        return self.request('POST', path, params, body)

    def put(self, path, params=None, body=None):
        return self.request('PUT', path, params, body)