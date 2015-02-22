# shell-messenger
Interface with  your facebook friends via the command line, so you can pretend to be doing work while really eschewing corporate duties!

Usage
------
1. Install dependencies:
brew install phantomjs
pip install splinter (installs selenium as well)
pip install pillow
pip install html5lib
pip install requests
pip install colorama 

2. Create login information file. Email in first line, password in second. 
3. Run listener: python listener.py <login.txt>
4. Run sender: python sender.py <login.txt> 

