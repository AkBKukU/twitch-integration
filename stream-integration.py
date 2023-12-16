#!/usr/bin/python3
# Production Imports
#from stream.api_twitch import APItwitch
#from stream.output_dectalk import OUTDectalk

# Test Imports
from stream.api_twitch_test import APItwitchTest as APItwitch
from stream.output_base import OUTBase as OUTDectalk

import asyncio


outtest = OUTDectalk()


print("Starting Stream Integration")
twitch = APItwitch("/home/akbkuku/client.json")
twitch.register_interact(outtest.receive_interact)
twitch.register_donate(outtest.receive_donate)

asyncio.run(twitch.connect())

input('press ENTER to close...')

asyncio.run(twitch.disconnect())

