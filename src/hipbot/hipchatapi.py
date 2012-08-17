from urllib import urlencode
#from yaml import load, dump
from hipchataction import do_hipchat_actions
import json
import isodate
import requests
import os

class HipchatError(Exception):
    pass

class HipchatConnection(object):

    def __init__(self, api_token=None):
        self.session = requests.session(
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.token = api_token or os.getenv('HIPCHAT_TOKEN')
        if not self.token:
        	raise HipchatError, 'Missing API credentials'

    def request(self, method, path, params=None, body=None):

        if not path.startswith('/'):
            path = '/' + path
        url = 'https://api.hipchat.com/v1' + path

        params = params or {}
        params.update({'format': 'json', 'auth_token': self.token})
        url += '?' + urlencode(params)
        response = self.session.request(method, url, data=body)
        if response.status_code != 200:
            # TODO: confirm that Hipchat never returns a 201, for example, when
            # creating a new object. If it does, then we shouldn't restrict
            # ourselves to a 200 here.
            raise HipchatError(response.text)
        return response.text

    def get(self, path, params=None):
        return json.loads(self.request('GET', path, params))

    def post(self, path, params=None, body=None):
        return self.request('POST', path, params, body)

    def put(self, path, params=None, body=None):
        return self.request('PUT', path, params, body)

class HipchatRequest(object):

    def __init__(self):

        self.conn = HipchatConnection()
        self.get_room_list()
        self.get_recent_messages()

    def get_room_list(self):
        _path = '/rooms/list'
        rooms = self.conn.get(_path)
        self.roomlist = {}
        for room in rooms['rooms']:
            self.roomlist.update({str(room['name']): room['room_id']})


    def send_message(self, msg):
        _path = '/rooms/message'
        _params = {}
        
        from_who = msg['from']
        color = msg['color']
        room_id = None
        #if 'from' in msg.keys():
        #    from_who = msg['from']
        #else:
        #    from_who = 'Trello'
        #color = msg['color'] or 'yellow'

        if 'room' in msg.keys():
            desired_room = msg['room'].split(':')[1]
            if desired_room in self.roomlist.keys():
                room_id = self.roomlist[desired_room]
        elif 'room_id' in msg.keys():
            room_id = msg['room_id']
        else:
            room_id = None  

        if room_id:
            _params.update({'room_id': room_id})
            _params.update({'from': from_who})
            _params.update({'message_format': msg['format']})
            _params.update({'color': color})
            _params.update({'message': msg['text']}) 
            self.conn.post(_path, _params)

    def get_recent_messages(self):
        _path = '/rooms/history'
        _params = {}

        for room, room_id in self.roomlist.items():
            _params.update({'room_id': room_id})
            _params.update({'date': 'recent'})
            _params.update({'format': 'json'})
            msgs = self.conn.get(_path, _params)
            msg_tosend = do_hipchat_actions(msgs, room_id)
            if msg_tosend:
                print 'msgs: ' + str(len(msg_tosend))
                for msg in msg_tosend:
                    self.send_message(msg)





if __name__ == '__main__':
    req = HipchatRequest()
    req.get_room_list()
    msg = {'text': 'Test message 1', 'room': 'hipchat:Test Room', 'format': 'text'}
    req.send_message(msg)
    print req.roomlist
