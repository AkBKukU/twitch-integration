#!/usr/bin/python3

# Requires
# sudo apt-get install python3 python3-dev festival festival-dev
# pip install pyfestival

from stream.output_base import OUTBase

import festival

class OUTFestival(OUTBase):
    """Simple CLI output receiver
    """

    def __init__(self):
        self.service_name = "Festival"

    def receive_donate(self,from_name,amount,message):
        """Output message as audio for donate"""
        festival.sayText(from_name+" gave "+amount+" and said "+message)
        return

    def receive_interact(self,from_name,kind,message):
        """Output message as audio for interaction"""
        festival.sayText(from_name+" gave "+kind+" and said "+message)
        return
