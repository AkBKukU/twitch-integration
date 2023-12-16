#!/usr/bin/python3
from stream.api_twitch import APItwitch

from pprint import pprint
import asyncio
from uuid import UUID
import json
import time
import os

from multiprocessing import Process, Manager, Value, Array

class APItwitchTest(APItwitch):

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "TwitchTest"




    def process(self):
        while(True):
            print("This is a test of processing")
            time.sleep(1)

            points="test/points.json"
            if os.path.isfile(points):
                with open(points, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_points("1337", data))
                os.rename(points,"test/done_points.json")

            bits="test/bits.json"
            if os.path.isfile(bits):
                with open(bits, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_bits("1337", data))
                os.rename(bits,"test/done_bits.json")

            subs="test/subs.json"
            if os.path.isfile(subs):
                with open(subs, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_subs("1337", data))
                os.rename(subs,"test/done_subs.json")

        return

    def get_cont(self):
        return self.cont

    async def connect(self):
        """Return name of service"""
        print("Not Connecting to twitch")

        self.procs = []
        proc = Process(target=self.process, args=())  # instantiating without any argument
        self.procs.append(proc)

        proc.start()
        return

    async def disconnect(self):
        print("Not Disconnecting to twitch")

        for proc in self.procs:
            proc.terminate()
        return

