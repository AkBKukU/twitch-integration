#!/usr/bin/python3
# Production Imports
from stream.api_twitch import APItwitch
from stream.api_youtube import APIyoutube
#from stream.output_dectalk import OUTDectalk
#from stream.output_call import OUTCall


# Test Imports
#from stream.api_twitch_test import APItwitchTest as APItwitch
from stream.output_base import OUTBase as OUTDectalk

from stream.api_http import APIhttp

import asyncio
import signal
from pathlib import Path

global loop_state
loop_state = True

async def main_loop():
    """ Blocking main loop to provide time for async tasks to run"""
    global loop_state
    while loop_state:
        await asyncio.sleep(1)


async def main():
    """ Start connections to async modules """

    # Setup CTRL-C signal to end programm
    signal.signal(signal.SIGINT, exit_handler)
    print('Press Ctrl+C to exit program')

    # Start async modules
    L = await asyncio.gather(
        twitch.connect(),
        youtube.connect(),
        main_loop()
    )


def exit_handler(sig, frame):
    """ Handle CTRL-C to gracefully end program and API connections """
    global loop_state
    print('You pressed Ctrl+C!')
    loop_state = False



# Setup modules
outtest = OUTDectalk()
#outcall = OUTCall("192.168.1.219")
http = APIhttp()
twitch = APItwitch(str(Path.home())+"/.api/twitch.json")
youtube = APIyoutube(
    key_path=str(Path.home())+"/.api/youtube.json",
    auth_token=str(Path.home())+"/.api/youtube_auth.json"
)

# Connect modules
twitch.register_interact(outtest.receive_interact)
twitch.register_chat(outtest.receive_chat)
twitch.register_chat(http.receive_chat)
#twitch.register_interact(outcall.receive_interact)
twitch.register_donate(outtest.receive_donate)
youtube.register_chat(http.receive_chat)

# Start non async
http.connect()

asyncio.run(main())

# Run after CTRL-C
http.disconnect()
#asyncio.run(twitch.disconnect())


