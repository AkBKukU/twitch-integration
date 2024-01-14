#!/usr/bin/python3
from stream.key import APIKey

import sys, os
import asyncio
from datetime import datetime

class APIbase(APIKey):
    """API Base for signal emitters

    Manages loading API keys, logging, and registering signal recievers
    """

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "Base"
        self.auth_token = None
        self.api = None
        self.callbacks_donate=[]
        self.callbacks_interact=[]
        self.callbacks_chat=[]
        self.tasks={}

    def log(self,filename,text):
        """logging output for data"""
        log_path="log/"+self.service_name
        # Make log dir if not there
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # Build filename
        filepath=log_path+"/"+str(datetime.now().isoformat()).replace(":","-")+"_"+filename+".log"
        # Write data
        with open(filepath, 'w', encoding="utf-8") as output:
            output.write(text)
        return

    def name(self):
        """Return name of service"""
        return self.service_name

# Internal Function Timing

    async def delay(self, time_ms, callback):
        """ Delay execution of callback function """
        await asyncio.sleep(time_ms/1000.0)
        await callback()

    def delay_callback(self, name, time_ms, callback):
        """ Register delayed callback  """
        self.tasks[name] = asyncio.ensure_future(self.delay(time_ms, callback))

    async def cancel_delays(self):
        """ Delay execution of callback function """
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print("Emded task")

# API Connection

    def connect(self):
        """Dummy service connection"""
        print("No service to connect to.")
        return

    def disconnect(self):
        """Dummy service disconnect"""
        print("No service to disconnect from.")
        return

# Signals Chat

    def register_chat(self,callback):
        """Store callback receiver for chat"""
        self.callbacks_chat.append(callback)
        return

    def emit_chat(self,data):
        """Call stored receivers for chat"""
        for callback in self.callbacks_chat:
            callback(data)
        return

    def receive_chat(self,data):
        """Output message to CLI for chat"""
        print(data["from"]+" gave "+str(data["donate"])+" and said "+data["text"])
        return

# Signals Donate

    def register_donate(self,callback):
        """Store callback receiver for donation"""
        self.callbacks_donate.append(callback)
        return

    def emit_donate(self,from_name,amount,message):
        """Call stored receivers for donation"""
        for callback in self.callbacks_donate:
            callback(from_name,amount,message)
        return

    def receive_donate(self,from_name,amount,message):
        """Output message to CLI for donate"""
        print(from_name+" gave "+amount+" and said "+message)
        return

# Signals Interact

    def register_interact(self,callback):
        """Store callback receiver for interation"""
        print("register_interact")
        self.callbacks_interact.append(callback)
        return

    def emit_interact(self,from_name,kind,message):
        """Call stored receivers for interaction"""
        for callback in self.callbacks_interact:
            callback(from_name,kind,message)
        return

    def receive_interact(self,from_name,kind,message):
        """Output message to CLI for interaction"""
        print(from_name+" did "+kind+" and said "+message)
        return
