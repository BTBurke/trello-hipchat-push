#!/usr/bin/env python

from trellobot import TrelloRequest, TrelloAction
from hipbot import HipchatRequest

def mainloop():
	req = TrelloRequest()
	print req.data
	actions = TrelloAction(req.data)
	req.process_api_actions(actions.api_actions)

	req2 = HipchatRequest()
	print actions.to_hipchat
	for board_update in actions.to_hipchat:
		for msg in board_update:
			req2.send_message(msg)

if __name__ == '__main__':
	mainloop()

