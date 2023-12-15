#!/usr/bin/python3
from stream.api_twitch import APItwitch
import asyncio

from stream.output_dectalk import OUTDectalk

outtest = OUTDectalk()


print("Starting Stream Integration")
twitch = APItwitch("/home/akbkuku/client.json")
twitch.register_interact(outtest.receive_interact)
twitch.register_donate(outtest.receive_donate)

asyncio.run(twitch.connect())

input('press ENTER to close...')

asyncio.run(twitch.disconnect())

