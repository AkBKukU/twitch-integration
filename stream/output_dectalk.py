#!/usr/bin/python3
from stream.output_base import OUTBase

import serial
import re

class OUTDectalk(OUTBase):

    def __init__(self):
        """Init with file path"""
        super().__init__()
        self.service_name = "DECTalk"

    def write(self,text):
        text = self.clean(text)
        ser = serial.Serial('/dev/ttyUSB0',9600,timeout=1)  # open serial port
        ser.write( bytes("[:punct none]"+str(text)+str('[:nh][:dv ap 90 pr 0].[:rate 140]END OF LINE.[:np][:pp 0 :cp 0][:rate 200][:say line][:punct none][:pitch 35][:phoneme off][:volume set 33]\r\n'),'ascii',errors='ignore') )
        return


    def clean(self,text):
        text = text.replace("google", "")
        text = text.replace(":period", ":rate")
        text = text.replace(":comma", ":rate")
        text = re.sub(":volume\s+set", ":np] . Volume Override[:rate ",text)
        text = text.replace("%p","[:phoneme arpabet speak on]").replace("%P","[:phoneme arpabet speak on]")

        return text


    def receive_donate(self,from_name,amount,message,benefits=None):
        if amount.endswith("b"):
            amount = amount.replace("b")
            if int(amount) < 100:
                return

            # Bits Donate
            self.write(from_name+" says "+message)


        if amount.endswith("s"):
            # Sub
            self.write(message)
        return

    def receive_interact(self,from_name,kind,message):
        if kind == "API Test":
            self.write(from_name+" did "+kind+" and said "+message)
        return
