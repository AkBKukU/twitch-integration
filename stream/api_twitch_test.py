#!/usr/bin/python3
from stream.api_twitch import APItwitch

from pprint import pprint
import asyncio
from uuid import UUID
import json
import time
import os
from datetime import datetime

from multiprocessing import Process, Manager, Value, Array

class APItwitchTest(APItwitch):
    """Twitch API test

    An empty twitch test class that extends the full class. Looks for json
    data from log files in "test/" folder.
    """

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "TwitchTest"
        self.procs = []


    def process(self):
        """multiprocess background task to look for test files"""
        while(True):
            time.sleep(1)

            # Check for point redeem
            points="test/points.json"
            if os.path.isfile(points):
                with open(points, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_points("1337", data))
                os.rename(points,"test/done_points.json")

            # Check for bit cheer
            bits="test/bits.json"
            if os.path.isfile(bits):
                with open(bits, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_bits("1337", data))
                os.rename(bits,"test/done_bits.json")

            # Check for subs
            subs="test/subs.json"
            if os.path.isfile(subs):
                with open(subs, 'r') as f:
                    data = json.load(f)
                    asyncio.run(self.callback_subs("1337", data))
                os.rename(subs,"test/done_subs.json")

            message={
                    "from": "Fred",
                    "color": "#FF0000",
                    "text": "Right",
                    "time": str(datetime.now().isoformat()).replace(":","-"),
                    "donate": 0
                }
            self.emit_chat(message)
        return


    async def connect(self):
        """Override parent API connection and start background test"""
        print("Not Connecting to twitch")

        # Create background process
        proc = Process(target=self.process, args=())  # instantiating without any argument
        self.procs.append(proc)

        # Start test checking
        proc.start()
        return

    async def disconnect(self):
        """Override parent API connection and end background test"""
        print("Not Disconnecting to twitch")

        # Force any background processes to end
        for proc in self.procs:
            proc.terminate()
        return

