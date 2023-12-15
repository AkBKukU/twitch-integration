#!/usr/bin/python3
from stream.api_base import APIbase

from twitchAPI.twitch import Twitch
from twitchAPI.pubsub import PubSub
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope

from pprint import pprint
import asyncio
from uuid import UUID
import json


class APItwitch(APIbase):

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "Twitch"


    async def connect(self):
        """Return name of service"""
        print("Connect to twitch")
        self.api = await Twitch(self.client_id, self.client_secret)

        # Scope for API to allow reading different data types
        target_scope = [
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.BITS_READ,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS
        ]
        auth = UserAuthenticator(self.api, target_scope, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = await auth.authenticate()
        # add User authentication
        await self.api.set_user_authentication(token, target_scope, refresh_token)

        self.user = await first(self.api.get_users(logins=['TechTangents']))
        pprint(self.user.id)

        # starting up PubSub
        self.pubsub = PubSub(self.api)
        self.pubsub.start()

        self.uuid_points = await self.pubsub.listen_channel_points(self.user.id, self.callback_points)
        self.uuid_bits = await self.pubsub.listen_bits(self.user.id, self.callback_bits)
        self.uuid_subs = await self.pubsub.listen_channel_subscriptions(self.user.id, self.callback_subs)
        return

    async def disconnect(self):
        await self.pubsub.unlisten(self.uuid_points)
        await self.pubsub.unlisten(self.uuid_bits)
        await self.pubsub.unlisten(self.uuid_subs)
        self.pubsub.stop()
        await self.api.close()

    async def callback_points(self, uuid: UUID, data: dict):
        #print('got callback for UUID ' + str(uuid))
        self.log("callback_points",json.dumps(data))
        self.emit_interact(data['data']['redemption']['user']['display_name'],
                            data['data']['redemption']['reward']['title'],
                            data['data']['redemption']['user_input']
                            )
        return

    async def callback_bits(self, uuid: UUID, data: dict):
        #print('got callback for UUID ' + str(uuid))
        self.log("callback_bits",json.dumps(data))

        self.emit_donate(data['data']['user_name'],
                            data['data']['bits_used']+"b",
                            data['data']['chat_message']
                            )
        return

    async def callback_subs(self, uuid: UUID, data: dict):
        #print('got callback for UUID ' + str(uuid))
        self.log("callback_subs",json.dumps(data))

        sub=data

        sub_type=""
        if (str(sub['sub_plan']) == "1000"):
            sub_type="tier one"
        if (str(sub['sub_plan']) == "2000"):
            sub_type="tier two"
        if (str(sub['sub_plan']) == "3000"):
            sub_type="tier three"
        if (str(sub['sub_plan']) == "Prime"):
            sub_type="prime"

        sub_len=""
        if ('benefit_end_month' in sub and sub['benefit_end_month'] != 0):
            sub_len="for "+str(int(sub['benefit_end_month'])+1)+" months"
        if ('multi_month_duration' in sub and sub['multi_month_duration'] > 1):
            sub_len="for "+str(sub['multi_month_duration'])+" months"

        line=""
        if str(data['context']) ==  "subgift":
            line=str(data['display_name'])
            line += " gave a "+sub_type+" gift sub "+sub_len+" to "+str(data['recipient_display_name'])
        elif str(data['context']) ==  "anonsubgift" or str(data['context']) ==  "anonresubgift":
            line += "Anonymous gifter gave a "+sub_type+" gift sub "+sub_len+" to "+str(data['recipient_display_name'])
        else:
            line=str(data['display_name'])
            line += " subbed as "+sub_type+" "+sub_len+" and says "+str(data['sub_message']['message'])

        self.emit_donate(data['data']['user_name'],
                            str(sub['sub_plan'])+"s",
                            line
                            )
        return

