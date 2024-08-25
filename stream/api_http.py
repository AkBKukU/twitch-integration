#!/usr/bin/python3
from stream.api_base import APIbase

from flask import Flask
from flask import request
from flask import send_file
from flask import redirect
from flask import make_response

from multiprocessing import Process

import os
import bleach
import json
from datetime import datetime

class APIhttp(APIbase):
    """Twitch API with signal emitters for bits, subs, and point redeems

    Manages authentication and creating messages from API events to     use elsewhere
    """

    def __init__(self,key_path=None,log=False):
        super().__init__(key_path)
        """Init with file path"""
        self.service_name = "HTTP"

        self.app = Flask("The Web: Now with 100% More OOP")

        # Define routes in class to use with flask
        self.app.add_url_rule('/','home', self.index)
        self.app.add_url_rule('/chat/','chat', self.chat)
        self.app.add_url_rule('/chat/chat.json','data', self.chatJsonChat)
        self.app.add_url_rule('/read/','read', self.read)
        self.app.add_url_rule('/read/read.css','read-css', self.readCss)
        self.app.add_url_rule('/read/chat.json','read-data', self.readJsonChat)
        self.app.add_url_rule('/window/','window', self.window)
        self.app.add_url_rule('/window/window.css','window-css', self.windowCss)
        self.app.add_url_rule('/window/window.js','window-js', self.windowJs)
        self.app.add_url_rule('/window/chat.json','window-chat', self.windowJsonChat)
        self.app.add_url_rule('/window/subs.json','window-subs', self.windowJsonSubs)
        self.app.add_url_rule('/window/poll.json','window-poll', self.windowJsonPoll)

        # Set headers for server
        self.app.after_request(self.add_header)

        self.chat = []
        self.subs = []
        self.poll = {}
        self.poll_output = {}
        self.poll_valid = []
        self.poll_threshold = 3
        self.json_chat= '/tmp/stream_http_chat.json'
        self.json_subs= '/tmp/stream_http_subs.json'
        self.json_poll= '/tmp/stream_http_poll.json'
        self.host = "0.0.0.0"

        

    def set_host(self,host_ip):
        self.host = host_ip

    def add_header(self,r):
        """
        Force the page cache to be reloaded each time
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    async def poll_check(self):
        # If there are 10 identical messages in self.poll start poll and add message to valid
        # after, if there are 10 other identical messages add new valid option and display
        # if voter messages after voting ignore, unless valid vote number
        print("####### Poll Check")
        poll_count={}
        for k, v in self.poll.items():
            if v not in poll_count:
                poll_count[v] = 1
            else:
                poll_count[v] += 1

        for poll_option in poll_count:
            if poll_count[poll_option] >= self.poll_threshold:
                if poll_option not in self.poll_valid:
                    self.poll_valid.append(poll_option)

        if self.poll_valid and self.poll_output["valid"] == False:
            print("####### Poll started with valid options:")
            self.poll_output["valid"] = True
        if self.poll_valid:
            poll_data = {}
            for opt in self.poll_valid:
                if opt not in poll_count:
                    poll_count[opt] = 0
                print(opt+": "+str(poll_count[opt]))
                poll_data[opt] = poll_count[opt]
            self.poll_output["data"] = poll_data

            with open(self.json_poll, 'w', encoding="utf-8") as output:
                output.write(json.dumps(self.poll_output))

            self.poll_output["remaining"] -= 1
            if (self.poll_output["remaining"] < 1):
                # Poll over
                self.delay_callback("poll_clear", 10000, self.poll_clear)

                win = max(poll_count, key=poll_count.get)
                # Send data to receivers
                self.emit_interact("api",
                    "Poll Results",
                    win
                    )

                self.receive_donate("api","1s","Poll Over ["+win+"] Wins")
                return

            # Valid poll started, display with html

        self.delay_callback("poll_check", 1000, self.poll_check)
        return

    async def poll_clear(self):
        self.poll = {}
        self.poll_valid = []
        self.poll_output = {}
        self.poll_output["title"] = "Dynamic Poll"
        self.poll_output["remaining"] = 30
        self.poll_output["valid"] = False
        with open(self.json_poll, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.poll_output))
        self.delay_callback("poll_check", 1000, self.poll_check)
        return

    def poll_vote(self, from_name, text):
        return_state = "show"

        ## Change Vote
        # Set vote if matches valid index
        #try:
        #    if int(text) < len(self.poll_valid)+1 and int(text) > 0:
        #        self.poll[from_name] = self.poll_valid[int(text)]
        #        return return_state
        #except ValueError:
        #    pass

        # Haven't chated since last poll
        if from_name not in self.poll:
            # record anything
            self.poll[from_name] = text

            if self.poll_valid:
                win = max(self.poll_output["data"], key=self.poll_output["data"].get)
                if win == text:
                    self.poll_output["remaining"] -= 2
            return return_state

        ## Change Vote
        # Set vote if matches valid
        if text in self.poll_valid:
            self.poll[from_name] = text
            return return_state

        # Update vote if not valid
        if self.poll[from_name] not in self.poll_valid:
            self.poll[from_name] = text
            return return_state

        # No valid votes yet, update vote
        if not self.poll_valid:
            self.poll[from_name] = text
            return return_state

        return "show"

    async def connect(self):
        """ Run Flask in a process thread that is non-blocking """
        print("Starting Flask")
        self.web_thread = Process(target=self.app.run, kwargs={"host":self.host,"port":5001})
        self.web_thread.start()
        self.delay_callback("poll_clear", 100, self.poll_clear)

    def disconnect(self):
        """ Send SIGKILL and join thread to end Flask server """
        self.web_thread.terminate()
        self.web_thread.join()

    def poll_config(self,title):
        self.poll_output["title"] = title
        self.poll_output["remaining"] += 60


    def index(self):
        """ Simple class function to send HTML to browser """
        return """
<a href="/chat/"><h2>Chat</h2></a>
<a href="/read/"><h2>Read</h2></a>
<a href="/window/"><h2>Window</h2></a>
        """

    def read(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/chat-read.html")

    def readCss(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/read.css")

    def chat(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/chat-view.html")

    def readJsonChat(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_chat)

    def chatJsonChat(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_chat)

    def window(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/window.html")

    def windowCss(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/window.css")

    def windowJs(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/window.js")

    def windowJsonChat(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_chat)

    def windowJsonSubs(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_subs)

    def windowJsonPoll(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_poll)

    def receive_donate(self,from_name,amount,message,benefits=None):
        """Output message to CLI for chat"""
        message = bleach.clean(message,tags={})

        print ("something Recieved: "+amount)
        # Subs
        if amount.endswith("b"):
            # No action on bits
            return

        print ("HTTP Sub Recieved")

        self.subs.append({"timestamp":str(datetime.now().isoformat()).replace(":","-"),"from":from_name, "text":message})

        if len(self.subs) > 30:
            self.subs.pop(0)

        with open(self.json_subs, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.subs))
        return

    def receive_chat(self,data):
        """Output message to CLI for chat"""
        data["text"] = bleach.clean(data["text"],tags={})
        self.chat.append(data)
        if self.poll_vote(data["from"], data["text"].lower().strip()) == "hide":
            return

        if len(self.chat) > 30:
            self.chat.pop(0)

        with open(self.json_chat, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.chat))
        return

    def receive_interact(self,from_name,kind,message):
        if kind == "Mod Chat Command":
            if message.find("!poll") == 0:
                self.poll_config(message.lower().replace("!poll","").strip())
                print("Poll title change: "+message)
