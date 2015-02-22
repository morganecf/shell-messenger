# -----------------------------------------
# This program allows you to interface with 
# your facebook friends via the command 
# line, so you can pretend to be doing work
# while really eschewing corporate duties!
# -----------------------------------------

# THIS COULD EASILY NOT WORK ON SOME VERSIONS
# OF FACEBOOK. 

# TODO : find some way to just recurse through 
# don't rely on div id's which may change 

# TODO: Switch to selenium? might not need splinter,
# which is just testing platform that uses selenium?

# TODO: optimization? time every method and see
# where lags are 

# TODO: customized error classes 
# TODO: Consolidate error messages in central object or class 

# TODO: Option to type in friend's username 
# or select from available friends 

## TODO: Might need to construct a thread 
# starting from last time you said something
# Otherwise could send several messages in a 
# row but spaced out by a lot of time, which
# would go in different li's 

## TODO: At end of session should restore 
# what user had for enter message type (enter or click)

# TODO: group threads 

## TODO: Detect connection timeout/refused

# TODO: log where keep track of errors, exceptions,
# things like if a button was unexpectedly invisible 

## TODO : for scraping operations have several ways of 
# doing things and try those in cascading exception 
# raising style. this way have lots of backup in case
# css/html changes 
 
# TODO: make tests and examples 

# TODO: Method to capture screenshot 

# Should use: is_element_present_by_id(id, wait_time)
# to wait a certain amount of time until the elem 
# is present (if javascript hasn't loaded yet) 

import re 
import json 
import requests 
import urllib
from urllib2 import URLError
from splinter import Browser
from bs4 import BeautifulSoup as soup 
from img2txt import handle_image_conversion
from splinter.exceptions import ElementDoesNotExist
from selenium.common.exceptions import StaleElementReferenceException

_user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11"
_base_url = "https://www.facebook.com"
_login_url = "https://login.facebook.com/login.php?login_attempt=1"
_msg_html = "<input type=\"hidden\" name=\"fb_dtsg\" value=\"(.*)\" autocomplete=\"off\" />"
_limit = 10
_base_msg_url = _base_url + "/messages/"
_url_regex = re.compile(r'<a href="(https://www\.facebook\.com/[^\s]*)"')
_friends_file = "friends.txt"

# _headers = {
# 	'Host': _base_url,
# 	'Origin': _base_url,
# 	'Referer': _base_url,
# 	'User-Agent': _user_agent
# }
_headers = {'Host':'www.facebook.com',
	'Origin':'http://www.facebook.com',
	'Referer':'http://www.facebook.com/',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11'}


def message_request(friend_id, my_id, fb_dtsg):
	friend_id = int(friend_id)
	my_id = int(my_id)
	url = "https://www.facebook.com/ajax/mercury/thread_info.php?&messages[user_ids][%d][limit]=%d&client=mercury&__user=%d&__a=1&__req=18&fb_dtsg=%s" % (friend_id, _limit, my_id, fb_dtsg)
	#print url 
	return url

def logged_in(url): return "login.php" not in url 

class Messenger:

	def __init__(self, username=None, password=None): 
		self.browser = Browser("phantomjs")
		self.session = requests.Session()

		self.my_id = None 
		self.content = None 

		if username and password:
			self.login(username, password)
			self.phantom_login(username, password)

		self.friends = self.__init_friends()
		self.aliases = self.__init_aliases()
		self.curr_url = None

		self.seen = set()


	# TODO: error handling in case id changes 
	# TODO: Need way of verifying that truly logged in
	# TODO: Need better way than while loop? eventual timeout? 
	def login(self, username, password):
		home_request = self.session.get(_base_url).text
		login_soup = soup(home_request, "html5lib")
		lsd = str(login_soup.find_all('input', attrs={"name": "lsd"})[0]['value'])
		login_data = {
		    'locale': 'en_US',
		    'non_com_login': '',
		    'email': username,
		    'pass': password,
		    'lsd': lsd
		}
		self.content = self.session.post(_login_url, data=login_data, verify=False)

	def phantom_login(self, username, password):
		try:
			self.browser.visit(_base_url)

			self.curr_url = self.browser.url
			inputs = self.browser.find_by_id("login_form")[0].find_by_tag("input")
			inputs[1].fill(username)
			inputs[2].fill(password)

			## OR maybe double check that enter button has both u_0_n and value=Log?
			# could have something else with id=u_0_n which is why it doesn't always work
			try:
				enter = self.browser.find_by_id("u_0_n").first
				enter.click()
			except:
				try:
					enter = self.browser.find_by_css("input[value='Log In']").first
					enter.click()
				except:
					try:
						enter = self.browser.find_by_css("input[type='submit']").first
						enter.click()
					except:
						print "Nothing works :("
						return

			# if not self.logged():
			# 	print "Login failed. Try again by restarting the app."
			self.curr_url = self.browser.url
			id_data = json.loads(self.browser.find_by_css("a.fbxWelcomeBoxName")["data-gt"])
			self.my_id = str(id_data["bmid"])
		except URLError:
			print "Connection refused: try restarting the app or logging in again."

	# TODO: Store message iD? 
	# TODO: What if send message without checking for reply?? 
	def fetch(self, friend):
		# Make sure logged in and able to see conten t
		if not self.content:
			print "You must be logged in to do that.", self.content 
			return

		# Check for alias 
		if self.aliases.get(friend):
			friend = self.aliases[friend]

		# Get corresponding id 
		friend_id = None 
		try:
			last_names = self.friends[friend]
			# Unambiguous friend specification 
			if len(last_names) == 1:
				friend_id = last_names[0][1]
			# Ambiguous friend specification - ask for last name
			else:
				last_name = raw_input("You have several friends named " + friend + ". What's their last name?")
				for last, fid in last_names:
					if last_name == last:
						friend_id = fid 
				if friend_id is None:
					raise KeyError
		except KeyError:
			username = raw_input("What's " + friend + "'s username?")
			#self.browser.visit()
			print username 
			return 
		
		# Get messages in json format 
		content_soup = soup(self.content.content, "html5lib")
		fb_dtsg = re.search(_msg_html, self.content.content).group(1).split('\"')[0]
		url = message_request(friend_id, self.my_id, fb_dtsg)
		data = self.session.get(url, headers=_headers, verify=False).text[9:]
		message_dict = json.loads(data)
		message_list = message_dict["payload"]["actions"]

		# Get unread messages 
		messages = []
		start = False 
		for message in message_list:
			isUnread = message["is_unread"]
			author = message["author"].split(':')[1]
			#if isUnread:
			start = True 
			if start:
				message_content = message["body"]
				timestamp = message["timestamp_datetime"]
				source = message["source_tags"]
				if "mobile" in source:
					source = "mobile"
				else:
					source = "chat"
				formatted = {"content": message_content, "timestamp": timestamp, "source": source}
				if author == self.my_id:
					formatted["author"] = "me"
				else:
					formatted["author"] = friend 
				mid = message["message_id"]
				if mid not in self.seen:
					attachments = message['attachments']
					if len(attachments) > 0:
						for att in attachments:
							att_type = att['attach_type']
							if att_type == 'sticker':
								img_url = att['url'].replace('\\/', '/')
							if att_type == 'photo':
								img_url = att['preview_url'].replace('\\/', '/')
							image = urllib.URLopener()
							image.retrieve(img_url, 'temp.png')
							handle_image_conversion('temp.png')
					else:
						messages.append(formatted)
					self.seen.add(mid)

		# TODO: need to make duplicate name checks etc 
		friend_url = _base_msg_url + self.friends[friend][0][2]
		self.browser.visit(friend_url)
		return messages 


	# TODO: Find way to wait (callback function) until 
	# reply button is visible ?
	# TODO: Send message to friend that d.n.e in inbox
	def send(self, friend, message):
		# Make sure logged in 
		# if not self.logged():
		# 	print "You must be logged in to do that."
		# 	return

		# Check for alias 
		if self.aliases.get(friend):
			friend = self.aliases[friend]

		# TODO: check for same names 
		username = self.friends[friend][0][2]

		try:
			friend_url = _base_msg_url + username
			if self.curr_url != friend_url:
				try:
					self.browser.visit(friend_url)
				# TODO: Is this really what this means? 
				except InvalidElementStateException:
					print "Friend", username, "does not exist."
					return 

			self.curr_url = self.browser.url 
			# Fill message body 
			self.browser.fill("message_body", message)

			# Find reply button 
			try:
				replies = self.browser.find_by_value("Reply")
			except ElementDoesNotExist:
				replies = self.browser.find_by_value("Reply All")
			if replies:
				reply = replies[0]
				# If reply button is invisible
				if not reply.visible:
					# Click checkbox to remove autosend
					self.browser.find_by_css("a[role='checkbox']")[0].click()
				reply.click()	
				self.curr_url = self.browser.url 
			else:
				print "Could not find reply button."
		except URLError:
			print "Connection refused: try restarting the app or logging in again."	

	# Get list of new messages you have 
	def new_messages(self):
		pass

	# Create name to user id mapping 
	def __init_friends(self):
		friends = {}
		# Check for friend file 
		try:
			friend_lines = open("friend_ids.tsv").read().splitlines()
			for line in friend_lines:
				name, fid, username = line.split('\t')
				# Store first name and potential last names with ids 
				first = name.split('_')[0]
				last = name.split('_')[1]
				try:
					friends[first].append((last, fid, username))
				except KeyError:
					friends[first] = [(last, fid, username)]
		# If friend file hasn't yet been created, go through 
		# recent friends and find their names/ids 				
		except IOError:
			friend_file = open("friend_ids.tsv", "w")	
			self.browser.visit(_base_msg_url)
			self.curr_url = self.browser.url 
			recent_users = self.browser.find_by_css("li._k-")
			for user in recent_users:
				try:
					fid = user['id'].split(':')[2]
					name = user.find_by_css("span.accessible_elem").text.lower() 
					username = user.find_by_css("a._k_")['href'].split("/")[-1]
					try:
						first = name.split()[0]
						last = name.split()[1]
					except IndexError:
						continue
					friend_file.write(first + '_' + last + '\t' + fid + '\t' + username + '\n')
					try:
						friends[first].append((last, fid, username))
					except KeyError:
						friends[first] = [(last, fid, username)]
				except StaleElementReferenceException:
					continue
			friend_file.close()
		return friends 

	# Used to initialize the aliases dictionary with 
	# friend names/usernames from previous sessions. 
	def __init_aliases(self):
		aliases = {}
		try:
			# Friends file should be in name,username format 
			with open(_friends_file, "r") as f:
				lines = f.read().splitlines()
				for line in lines:
					name, username = line.split(",")
					aliases[name] = username 
				return aliases 
		# If the file does not exist, create it 
		except IOError:
			f = open(_friends_file, "w")
			f.close()
			return {}

	def update_friend_file(self, name=None, username=None):
		with open(_friends_file, "a") as f:
			if name and username:
				f.write(name + "," + username + "\n")
			else:
				for name, username in self.aliases.iteritems():
					f.write(name + "," + username + "\n")


	def add_alias(self, username, name, force=False):
		# Check to see if name already exists 
		try:
			self.aliases[name]
			if force:
				raise KeyError
			else:
				print "The name already exists. Use force=True to overwrite."
		# If name exists, update dictionary and file 
		except KeyError:
			self.aliases[name] = username
			self.update_friend_file(name=name, username=username)

	def take_screenshot(self, path):
		location = self.browser.screenshot(path)
		print "Saved in:", location 



