#!/usr/bin/python3
from stream.api_base import APIbase

from pprint import pprint
import json


""" Youtube Live Chat API Logic

Init API:
1. Connect to API
2. Get list of live broadcasts
3. Check if is active

If active broadcast
1. Get initial list of chat messages
2. store page token
3. wait ms delay
4. requst chat update
5. goto 2


This means the youtube API is going to need its own rolling interupt for querying
the server to get updated chats. When the broadcast ends I suspect the API will
continue to provide blank page tokens and delays, some method may be needed to
check for when the stream ends.

"""
class APIyoutube(APIbase):
    """Twitch API with signal emitters for bits, subs, and point redeems

    Manages authentication and creating messages from API events to use elsewhere
    """

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "Youtube"


    async def connect(self):
        """Connect to Twith API"""
        print("Connect to youtube")

        return


    async def disconnect(self):
        """Gracefully disconnect from Twith API"""

        return


    async def callback_chat(self, chat: ChatMessage):
        message={
                "from": chat.user.name,
                "color": chat.user.color,
                "text": chat.text,
                "donate": chat.bits
            }

        self.log("callback_chat",json.dumps(message))
        self.emit_chat(message)
        return

