# coding: utf8
import codecs
import os
from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM
from subprocess import Popen
import sys
try:
    import json
except ImportError:
    import simplejson as json

import web


class Ping:
    """
    Recieve pings from Github Webhook API and perform actions.

    Examples of actions:
        - Run a script to deploy on your webserver. Yup.
        - Send a message to IRC (via an ircbot listening for UDP-messages). Yup.
        - Send an email.
        - Send a signal to an Arduino.

    TODO:
     - Provide deploy log
     - Send mail to commiter on error.

    Written in web.py
    """
    def __init__(self):
        pass
    
    def script_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    def url_allowed(self, url):
        for allowed_url, deploy_to in settings.REPOS.iteritems():
            if url == allowed_url:
                return True
        return False

    def POST(self):
        data = web.data()
        if not data:
            error = "Error: No payload in POST."
            return json.dumps({'result': error})
        try:
            data = json.loads(data)
        except (ValueError, TypeError):
            error = "Error: Got ping with non-JSON POST-data: \'" + str(post_data) + "\'"
            self.log(error)
            return json.dumps({'result': error})

        repo_url = data['repository']['url']
        repo_name = data['repository']['name']
        self.log("Got ping. Repo: " + repo_name + " Commit by: " + self.format_who(data['commits']) + ".")
        if not self.url_allowed(repo_url):
            not_allowed = "Repository URL \'" + repo_url + "\' not allowed." 
            self.log(not_allowed)
            return not_allowed

        # TODO: Make optional in settings
        self.update_repo(data['repository']['name'], repo_url)
        self.send_to_irc(data)

        return json.dumps({'result': "Thank you :-)"})

    def update_repo(self, name, url):
        if not settings.REPOS[url]:
            self.log("No deploy path defined.")
            return
        # run the deployscript
        # TODO: send clone url instead to support remote repos
        args = [settings.DEPLOY_SCRIPT_PATH, settings.REPOS[url], name]
        self.log("Updating repo: \'" + " ".join(args) + "\'")
        Popen(args)

    def format_who(self, commits):
        if len(commits) == 1:
            who = commits[0]['author']['name']
        else:
            who = set()  # unique entries
            for commit in commits:
                who.add(commit['author']['name'])
            who = ", ".join(who)
        return who.split()[0]

    def shorten_url(self, url): 
        if settings.BITLY_USERNAME and settings.BITLY_API_KEY:
            import bitly_api
            c = bitly_api.Connection(settings.BITLY_USERNAME,
                                     settings.BITLY_API_KEY)
            return c.shorten(url)['url']
        else:
            return url

    def format_for_irc(self, data):
        # String to be sent to irc.
        commit_msg = data['commits'][0]['message'].strip().split("\n")[0][:50]
        who = self.format_who(data['commits'])
        compare_url = self.shorten_url(data['compare'])
        if len(data['commits']) > 1:
            return "[{0}] *{1} made {2} new commits*: {3}".format(
                data['repository']['name'],
                who,
                len(data['commits']),
                compare_url).encode('utf8')
        return u"[{0}] {1} (by {2}): {3}".format(
            data['repository']['name'],
            commit_msg,
            who,
            compare_url).encode('utf8')

    def send_to_irc(self, data):
        # Send the message to snurr via UDP.
        data = self.format_for_irc(data)
        udp = socket(AF_INET, SOCK_DGRAM)
        udp.sendto(data, settings.IRC_BOT_HOST)

    def log(self, msg):
        # Log pings.
        log = codecs.open(self.script_path() + "/pings.log",
                          "a+",
                          encoding='utf-8')
        log.write(datetime.now().isoformat() + ": " + msg + "\n")
        log.close()
   

# import settings (full path to cur dir has to be on path).
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)
import settings

# define urls
urls = (
    '/', 'Ping',
)

# run app
app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
