from urllib import urlencode
from yaml import load, dump
from trelloaction import TrelloAction
import json
import isodate
import requests
import os

class TrelloError(Exception):
    pass

class TrelloConnection(object):

    def __init__(self, api_key=None, oauth_token=None, username=None):
        self.session = requests.session(
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.key = api_key or os.getenv('TRELLO_KEY')
        self.token = oauth_token or os.getenv('TRELLO_TOKEN')
        self.username = username or os.getenv('TRELLO_USERNAME')
        if not self.key or not self.token or not self.username:
        	raise TrelloError, 'Missing API credentials'

    def request(self, method, path, params=None, body=None):

        if not path.startswith('/'):
            path = '/' + path
        url = 'https://api.trello.com/1' + path

        params = params or {}
        params.update({'key': self.key, 'token': self.token})
        url += '?' + urlencode(params)
        response = self.session.request(method, url, data=body)
        if response.status_code != 200:
            # TODO: confirm that Trello never returns a 201, for example, when
            # creating a new object. If it does, then we shouldn't restrict
            # ourselves to a 200 here.
            raise TrelloError(response.text)
        return response.text

    def get(self, path, params=None):
        return json.loads(self.request('GET', path, params))

    def post(self, path, params=None, body=None):
        return self.request('POST', path, params, body)

    def put(self, path, params=None, body=None):
        return self.request('PUT', path, params, body)

class TrelloRequest(object):

	def __init__(self):

		self.conn = TrelloConnection()
		boards = self.find_monitored_boards()
		self.get_action_state()
		self.data = []

		for board in boards:
			self.data.append(self.get_latest_board_actions(board))

		self.flush_action_state()
		self.update_hipchat_connections()

	def process_api_actions(self, actions):
		
		if actions:
			for action in actions:
				if action['action'] == 'post':
					self.conn.post(action['path'], action['params'], action['body'])
					
	def update_hipchat_connections(self):
		_path = '/search'
		_params = {'query': 'hipchat'}
		out = {}
		data = self.conn.get(_path, _params)
		for room in data['cards']:
			out.update({str(room['idBoard']): str(room['name'])})
		with open('hipchat_connect.yaml', 'w') as fid:
			dump(out, fid)

	def find_monitored_boards(self):
		_path = '/members/' + self.conn.username
		all_boards = self.conn.get(_path)
		return_boards = []

		for boardID in all_boards['idBoards']:
			_path = '/board/' + boardID + '/closed'
			is_closed = self.conn.get(_path)
			_path = '/board/' + boardID + '/name'
			board_name = self.conn.get(_path)
			
			if board_name['_value'] == u'Welcome Board':
				continue
			if not is_closed['_value']:
				return_boards.append(boardID)
		return return_boards

	def get_action_state(self, fname='actionstate.yaml'):		
		try:
			with open(fname, 'r') as fid:
				self.state = load(fid) or {}
		except IOError:
			print "Unable to open state file: " + fname
		fid.close()

	def flush_action_state(self, fname='actionstate.yaml'):
		try:
			with open(fname, 'w') as fid:
				dump(self.state, fid)
		except IOError:
			print "Unable to write to state file: " + fname
		fid.close()

	def get_latest_board_actions(self, boardID):
		_path = '/board/' + boardID + '/actions'
		_params = None

		if not self.state or not boardID in self.state.keys():
			_params = {'limit': 3}
		else:
			_params = {'since': self.state[boardID]}

		

		update_data = self.conn.get(_path, _params)
		
		if len(update_data) > 0:
			self.state.update({str(boardID): str(update_data[0]['date'])})
			#print self.state

		
		return update_data


if __name__ == '__main__':
	
	req = TrelloRequest()
	#print req.data
	actions = TrelloAction(req.data)
	print actions.to_hipchat
	req.process_api_actions(actions.api_actions)
	
