#!/usr/bin/env python

from trellobot import TrelloRequest, TrelloAction
from hipbot import HipchatRequest

def mainloop():
	req = TrelloRequest()
	actions = TrelloAction(req.data)
	req.process_api_actions(actions.api_actions)

	req2 = HipchatRequest()
	for board_update in actions.to_hipchat:
		for msg in board_update:
			req2.send_message(msg)

if __name__ == '__main__':
	mainloop()

