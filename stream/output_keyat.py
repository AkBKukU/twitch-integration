#!/usr/bin/python3
from stream.api_base import APIbase
from stream.keyat.interface import Interface as KAT
import re


class OUTKAT(APIbase):
    """Simple CLI output receiver
    """

    def __init__(self,serial_port='/dev/ttyUSB0'):
        super().__init__(None)
        self.service_name = "KeyAT"
        self.banned = [
            "q",
            "quit",
            ]
        self.remove = [
            "\\",
            "quit",
            "save",
            "restore",
            "restart",
            "restar",
            "script",
            "resta",
            "q.",
            ".q",
            ".",
            ]
        self.serial_port = serial_port

    def receive_chat(self,data):
        """Output message to CLI for donate"""
        keyat = KAT(self.serial_port)
        keyat.send(data["from"]+": "+data["text"]+"\n")
        return

    def receive_donate(self,from_name,amount,message):
        """Output message to CLI for donate"""
        keyat.send(from_name+" gave "+amount+" and said "+message)
        return

    def receive_interact(self,from_name,kind,message):
        """Output message to CLI for interaction"""
        keyat = KAT(self.serial_port)
        if kind == "Send Command":

            message = message.encode("ascii",errors="ignore").decode()
            message = re.sub('\\bq\\b', '', message)
            message = message.replace('~', '')
            message = message.replace('^', '')
            message = message.strip()
            message = message.lower()
            if message in self.banned:
                return

            for bad in self.remove:
                if bad in message:
                    return
            keyat.send(message[:32]+"\n")
            print("Command (from [" +from_name+ "]): " + message[:32])
        return



    def receive_donate(self,from_name,amount,message,benefits=None):
        """Respond to bit and sub messages"""

        message = message.strip()
        message = message.lower()

        # Bits
        if amount.endswith("b"):
            amount = amount.replace("b","")

            if int(amount) == 25:
                print("Maybe Restart: " + message)
                if "restart" in message:
                    keyat = KAT(self.serial_port)
                    keyat.send("restart\nY\n")
                    return
        return
