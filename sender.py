# Sends messages 

import sys 
import time 
import warnings 
from messenger import Messenger
from colorama import init
from colorama import Fore, Back, Style

init(autoreset=True)

login_info = open(sys.argv[1]).read().splitlines()
username = login_info[0]
password = login_info[1]

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	# Log in 
	print "Logging in..."
	m = Messenger(username=username, password=password)
	print "Logged in!"

	while True:
		# Get friend to talk to 
		friend = raw_input("Who do you want to talk to? ")
		# Get message to send 
		message = raw_input("What do you want to tell " + friend + "?")

		m.send(friend, message)




# my id: 1326450295
# my id: 1664490365
