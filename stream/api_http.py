#!/usr/bin/python3
from stream.api_base import APIbase

from flask import Flask
from flask import request
from flask import send_file
from flask import redirect
from flask import make_response

from multiprocessing import Process

import os
import json

class APIhttp(APIbase):
    """Twitch API with signal emitters for bits, subs, and point redeems

    Manages authentication and creating messages from API events to use elsewhere
    """

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        self.service_name = "HTTP"

        self.app = Flask("The Web: Now with 100% More OOP")

        # Define routes in class to use with flask
        self.app.add_url_rule('/','home', self.index)
        self.app.add_url_rule('/chat/','chat', self.chat)
        self.app.add_url_rule('/chat/data.json','data', self.data)

        # Set headers for server
        self.app.after_request(self.add_header)

        self.chat = []
        self.json_data= '/tmp/stream_http_data.json'

    def add_header(self,r):
        """
        Force the page cache to be reloaded each time
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r



    def connect(self):
        """ Run Flask in a process thread that is non-blocking """
        self.web_thread = Process(target=self.app.run, kwargs={"host":"0.0.0.0","port":5001})
        self.web_thread.start()

    def disconnect(self):
        """ Send SIGKILL and join thread to end Flask server """
        self.web_thread.terminate()
        self.web_thread.join()



    def index(self):
        """ Simple class function to send HTML to browser """
        return """
<a href="/chat/"><h2>Chat</h2></a>
        """

    def chat(self):
        """ Simple class function to send HTML to browser """
        return send_file("stream/http/chat-view.html")

    def data(self):
        """ Simple class function to send JSON to browser """
        return send_file(self.json_data)




    def receive_chat(self,data):
        """Output message to CLI for chat"""
        self.chat.append(data)

        if len(self.chat) > 100:
            self.chat.pop(0)

        with open(self.json_data, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.chat))
        return
