#!/usr/bin/python3


class OUTBase(object):

    def __init__(self):
        """Init with file path"""
        self.service_name = "Base"

    def receive_donate(self,from_name,amount,message):
        print(from_name+" gave "+amount+" and said "+message)
        return

    def receive_interact(self,from_name,kind,message):
        print(from_name+" did "+kind+" and said "+message)
        return
