# shell-messenger
Interface with  your facebook friends via the command line, so you can pretend to be doing work while really eschewing corporate duties!

Install 
-------
You'll just be running the scripts, but to install the dependencies, do:
+ brew install phantomjs
+ pip install splinter (installs selenium as well)
+ pip install pillow
+ pip install html5lib
+ pip install requests
+ pip install colorama 

Run
-------
1. Create login information file. Email in first line, password in second. 
2. Run listener: python listener.py <login.txt>
3. Run sender: python sender.py <login.txt> 

Screenshots
------
![Alt text](https://github.com/morganecf/shell-messenger/convo.png "Chat with friends about your miserable cubicle existence")
![Alt text](https://github.com/morganecf/shell-messenger/ascii.png "We even do ascii art! Ironically invalidating the raison d'etre of this app as a means to circumvent the corporocratic eye")
