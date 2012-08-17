from yaml import load
import json
import re

class ActionParseError(Exception):
	pass

class TrelloAction(object):

	def __init__(self, data):

		self.data = data
		self.to_hipchat = []
		self.api_actions = []
		with open('hipchat_connect.yaml', 'r') as fid:
			self.hipchat_rooms = load(fid)

		for board_update in data:
			self.to_hipchat.append(self.parse_board_updates(board_update))

		self.to_hipchat = [upd for upd in self.to_hipchat if upd]


	def parse_board_updates(self, board_updates):

		return_updates = []
		if board_updates:
			for board_update in board_updates:
					ret = self.parse_single_update(board_update)
					if ret:
						return_updates.append(ret)

		return return_updates

	def parse_single_update(self, data):
		
		ret_text = ''
		
		boardID = data['data']['board']['id']
		who = data['memberCreator']['fullName']
		if who == 'TrelloBot':
			#dont send any updates for what the bot does
			return

		if data['type'] == 'updateCard':
			if 'listBefore' in data['data'].keys():
				# Card has moved
				what = ' moved <b>' + data['data']['card']['name'] + '</b>'
				where_from = ' from <b>' + data['data']['listBefore']['name'] + '</b>'
				where_to = ' to <b>' + data['data']['listAfter']['name'] + '</b>'
				ret_text = who + what + where_from + where_to
		
		if data['type'] == 'createCard':
			what = ' created card <b>' + data['data']['card']['name'] + '</b>'
			added_to = ' and added it to <b>' + data['data']['list']['name'] + '</b>'
			ret_text = who + what + added_to
		
		if data['type'] == 'commentCard':

			what = ' commented on card <b>' + data['data']['card']['name'] + '</b>'
		
			# for comments, see if we can linkify it
			#self.linkify(data['data']['text'], data['data']['card']['id'])
		
			ret_text = who + what

		if boardID in self.hipchat_rooms.keys() and ret_text:
			return {'room': self.hipchat_rooms[boardID], 'text': ret_text, 'format': 'html', 'from': 'Trello', 'color': 'yellow'}

	def linkify(self, text, cardId):
		
		def sub(text):
			text = text.group(0)
			text = text.replace('\\', '/')
			text = 'file://' + text.replace(' ', '%20')
			return text

		if len(re.findall('(O:.*)', text)) > 0:
			link = re.sub('(O:.*)', sub, text)
			_path = '/card/' + cardId + '/actions/comments'
			_action = 'post'
			_body = json.dumps({'text': link})
			self.api_actions.append({'path': _path, 'params': None, 'action': _action, 'body': _body})



