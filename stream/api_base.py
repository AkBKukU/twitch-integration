#!/usr/bin/python3
from stream.key import APIKey

import sys, os
import asyncio
from datetime import datetime

class APIbase(APIKey):

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "Base"
        self.api = None
        self.callbacks_donate=[]
        self.callbacks_interact=[]

    def log(self,filename,text):
        log_path="log/"+self.service_name
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        filepath=log_path+"/"+str(datetime.now().isoformat()).replace(":","-")+"_"+filename+".log"
        with open(filepath, 'w', encoding="utf-8") as output:
            output.write(text)
        return

    def name(self):
        """Return name of service"""
        return self.service_name

    def connect(self):
        """Return name of service"""
        print("No service to connect to.")
        return

    def disconnect(self):
        """Return name of service"""
        print("No service to disconnect from.")
        return

    def register_donate(self,callback):
        self.callbacks_donate.append(callback)
        return

    def emit_donate(self,from_name,amount,message):
        for callback in self.callbacks_donate:
            callback(from_name,amount,message)
        return


    def register_interact(self,callback):
        print("register_interact")
        self.callbacks_interact.append(callback)
        return

    def emit_interact(self,from_name,kind,message):
        for callback in self.callbacks_interact:
            callback(from_name,kind,message)
        return
