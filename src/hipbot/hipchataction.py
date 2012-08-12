
from actions.chucknorris import chucknorris

def do_hipchat_actions(msgs, room_id):
	action_msgs = []

	for msg in msgs['messages']:
		# look for Chuck Norris and deliver joke
		cn_msg = chucknorris(msg)
		if cn_msg:
			cn_msg.update({'room_id': room_id})
			action_msgs.append(cn_msg)

	return action_msgs

if __name__ == '__main__':
	test_msgs = {"messages":[{"date":"2012-08-11T21:20:17+0000","from":{"name":"Bryan Burke","user_id":139296},"message":"(chuck norris)"},{"date":"2012-08-11T21:20:33+0000","from":{"name":"Bryan Burke","user_id":139296},"message":"(chucknorris)"},{"date":"2012-08-12T00:40:23+0000","from":{"name":"Bryan Burke","user_id":139296},"message":"chuck norris"}]}
	print(do_hipchat_actions(test_msgs, '10000'))