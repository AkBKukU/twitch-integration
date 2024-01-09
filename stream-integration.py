#!/usr/bin/python3
# Production Imports
#from stream.api_twitch import APItwitch
#from stream.output_dectalk import OUTDectalk
#from stream.output_call import OUTCall


# Test Imports
from stream.api_twitch_test import APItwitchTest as APItwitch
from stream.output_base import OUTBase as OUTDectalk

#from stream.api_http import APIhttp

import asyncio
from pathlib import Path

async def main_loop():
    while True:
        await asyncio.sleep(1)

outtest = OUTDectalk()
#outcall = OUTCall("192.168.1.219")
#http = APIhttp()


print("Starting Stream Integration")
twitch = APItwitch(str(Path.home())+"/.api/twitch.json")
twitch.register_interact(outtest.receive_interact)
twitch.register_chat(outtest.receive_chat)
#twitch.register_chat(http.receive_chat)
#twitch.register_interact(outcall.receive_interact)

twitch.register_donate(outtest.receive_donate)

asyncio.run(twitch.connect())
#http.connect()

asyncio.run(main_loop())

#http.disconnect()

asyncio.run(twitch.disconnect())

