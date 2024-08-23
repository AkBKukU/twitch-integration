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

    Manages authentication and creating messages from API events to use elsewhere
    """

    def __init__(self,key_path=None,log=False):
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

        # Set headers for server
        self.app.after_request(self.add_header)

        self.chat = []
        self.subs = []
        self.json_chat= '/tmp/stream_http_chat.json'
        self.json_subs= '/tmp/stream_http_subs.json'

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
            self.chat.pop(0)

        with open(self.json_subs, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.subs))
        return

    def receive_chat(self,data):
        """Output message to CLI for chat"""
        data["text"] = bleach.clean(data["text"],tags={})
        self.chat.append(data)

        if len(self.chat) > 30:
            self.chat.pop(0)

        with open(self.json_chat, 'w', encoding="utf-8") as output:
            output.write(json.dumps(self.chat))
        return
