#!/usr/bin/python3
# Production Imports
#from stream.api_twitch import APItwitch
#from stream.output_dectalk import OUTDectalk
#from stream.output_call import OUTCall


# Test Imports
from stream.api_twitch_test import APItwitchTest as APItwitch
from stream.output_base import OUTBase as OUTDectalk

import asyncio
from pathlib import Path


outtest = OUTDectalk()
#outcall = OUTCall("192.168.1.219")


print("Starting Stream Integration")
twitch = APItwitch(str(Path.home())+"/.api/twitch.json")
twitch.register_interact(outtest.receive_interact)
twitch.register_chat(outtest.receive_chat)
#twitch.register_interact(outcall.receive_interact)

twitch.register_donate(outtest.receive_donate)

asyncio.run(twitch.connect())

input('press ENTER to close...\n')

asyncio.run(twitch.disconnect())

