import web
import simplejson as json
import urllib
from datetime import datetime
from subprocess import Popen
from socket import socket, AF_INET, SOCK_DGRAM
"""
Recieve pings from Github and:
    - Sync local repo and web.
    - Send a message to snurr (udp2irc-bot).

Written in web.py
"""

urls = (
    '/', 'ping',
)

class ping:
    # Configuration
    SCRIPT_PATH = '/opt/github-hooks-recieve/send_to_web.sh'
    WEB_PATH = '/var/www/neuf.no/new/'
    ALLOWED_REPO_URLS = ['https://github.com/neuf/main',]

    def POST(self):
        post_data = web.input()
        try:
            data = json.loads(post_data['payload'])
        except ValueError:
            self.log("Got ping with non-JSON POST-data" + post_data)
            exit()

        self.log("post_data: " + str(post_data))
        if data['repository']['url'] not in self.ALLOWED_REPO_URLS:
            self.log("Repository URL " + data['repository']['url'] + "not allowed, exiting.")
            exit()

        self.update_repo(data)
        self.send_to_irc(data)

        return "thank you :-)"

    def update_repo(self, data):
        # Update repository locally and push to web
        args = ['/bin/sh', self.SCRIPT_PATH, self.WEB_PATH, data['repository']['url']]
        self.log("Updating repo with command: \'" + " ".join(args) + "\'")
        p = Popen(args)

    def format_for_irc(self, data):
        # String to be sent to irc.
        
        who = ""
        if len(data['commits']) == 1:
            who = data['commits'][0]['author']['username']
        else:
            who = set() # unique entries
            for commit in data['commits']:
                who.add(commit['author']['username'])
            who = ", ".join(who)

        return "Github repo \'{0}\': {1} by {2}".format(data['repository']['name'],
                                               data['compare'],
                                               who)

    def send_to_irc(self, data):
        # Send the message to snurr via UDP.
        irc_data = self.format_for_irc(data)
        udp = socket(AF_INET, SOCK_DGRAM)
        udp.sendto(irc_data, ('127.0.0.1', 55666))

    def log(self, msg):
        # Log pings.
        log = open("/opt/github-hooks-recieve/pings.log", "a+")
        log.write(datetime.now().isoformat() + ": " + msg + "\n")
        log.close()
   
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
