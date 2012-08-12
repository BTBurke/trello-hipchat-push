import re
import datetime
import yaml
from apiconnection import APIConnection

def chucknorris(msg):
	if re.findall('chuck norris', msg['message'].lower()):

		if msg['from']['name'] == 'Chuck Norris':
			pass
		else:
			send_yes = compare_date(msg['date'])
			if send_yes:
				return get_joke()

def compare_date(date):
	with open('state/chucknorris.yaml', 'r') as fid:
		last = yaml.load(fid)

	current = parse_date(date)
	if 'date' in last.keys():
		last_date = parse_date(last['date'])
		if current - last_date > datetime.timedelta(0):
			send_yes = True
		else:
			send_yes = False
	else:
		send_yes = True

	if send_yes:
		with open('state/chucknorris.yaml', 'w') as fid:
			yaml.dump({'date': str(date)}, fid)
		return send_yes


def parse_date(date):
	day, time = date.split('T')
	time = time.split('+')[0]
	Y, M, D = day.split('-')
	HH, MM, SS = time.split(':')
	return datetime.datetime(int(Y), int(M), int(D), int(HH), int(MM), int(SS))

def get_joke():
	url = 'http://api.icndb.com/jokes/random'
	req = APIConnection(url)
	
	joke = req.get('')

	if joke:
		return format_msg(joke['value']['joke'])
	else:
		return None

def format_msg(joke):
	msg = {}
	msg.update({'from': 'Chuck Norris'})
	msg.update({'color': 'purple'})
	msg.update({'format': 'text'})
	msg.update({'text': joke + ' (chucknorris)'})
	return msg

if __name__ == '__main__':
	joke = get_joke()
	print joke



