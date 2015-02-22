# Listens for incoming messages 

# TODO: Thread to notify of new incoming messages
# TOOD: Thread to listen for keypress 

import sys 
import time 
import termios
import atexit
import warnings
from select import select
from messenger import Messenger
from colorama import init
from colorama import Fore, Back, Style

init(autoreset=True)

# save the terminal settings
fd = sys.stdin.fileno()
new_term = termios.tcgetattr(fd)
old_term = termios.tcgetattr(fd)

# new terminal setting unbuffered
new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)

# switch to normal terminal
def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

# switch to unbuffered terminal
def set_curses_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

def putch(ch):
    sys.stdout.write(ch)

def getch():
    return sys.stdin.read(1)

def getche():
    ch = getch()
    putch(ch)
    return ch

def kbhit():
    dr,dw,de = select([sys.stdin], [], [], 0)
    return dr <> []

def display_message(messages, friend): 
	if messages:
		#{"content": message_content, "timestamp": timestamp, "source": source, "author": author}
		for message in messages:
			msg = message["content"]
			timestamp = message["timestamp"]
			device = message["source"]
			sender = message["author"]

			print sender, 
			if sender == 'me':
				print(Fore.YELLOW + "\t" + msg),
			else:
				print(Fore.MAGENTA + "\t" + msg), 
			if sender == 'me':
				print "\t", timestamp
			else:
				print "\t", timestamp, "\t", device 
		return True 

with warnings.catch_warnings():
	warnings.simplefilter("ignore")

	atexit.register(set_normal_term)
	#set_curses_term()

	login_info = open(sys.argv[1]).read().splitlines()
	username = login_info[0]
	password = login_info[1]

	# Log in 
	print "Logging in..."
	m = Messenger(username=username, password=password)
	print "Logged in!"

	friend = None 

# Get friend to talk to 
def talk():
	set_normal_term()
	friend = raw_input("Who do you want to talk to? ")

	messages = m.fetch(friend)
	got_message = display_message(messages, friend)
	if not got_message:
		print "You have no new messages from", friend

	print "Waiting for more messages..."
	print "Press 1 to switch friends."
	set_curses_term()
	listen(friend)

def listen(friend):
	start = time.time()
	while True:
		if kbhit():
			ch = getch()
			if ch == '1':
				talk()
				break
		if time.time() - start >= 1:
			messages = m.fetch(friend)
			got_message = display_message(messages, friend)
			start = time.time()

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	
	talk()








