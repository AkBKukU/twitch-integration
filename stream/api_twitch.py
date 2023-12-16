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
    """Twitch API with signal emitters for bits, subs, and point redeems

    Manages authentication and creating messages from API events to use elsewhere
    """

    def __init__(self,key_path=None,log=False):
        """Init with file path"""
        super().__init__(key_path)
        self.service_name = "Twitch"


    async def connect(self):
        """Connect to Twith API"""
        print("Connect to twitch")
        self.api = await Twitch(self.client_id, self.client_secret)

        # Scope for API to allow reading different data types
        target_scope = [
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.BITS_READ,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS
        ]
        # Build user auth
        auth = UserAuthenticator(self.api, target_scope, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = await auth.authenticate()
        # add User authentication
        await self.api.set_user_authentication(token, target_scope, refresh_token)

        # Get user for channel to watch
        self.user = await first(self.api.get_users(logins=['TechTangents']))

        # Starting up PubSub
        self.pubsub = PubSub(self.api)
        self.pubsub.start()

        # Register callbacks for pubsub actions
        self.uuid_points = await self.pubsub.listen_channel_points(self.user.id, self.callback_points)
        self.uuid_bits = await self.pubsub.listen_bits(self.user.id, self.callback_bits)
        self.uuid_subs = await self.pubsub.listen_channel_subscriptions(self.user.id, self.callback_subs)

        return

    async def disconnect(self):
        """Gracefully disconnect from Twith API"""

        # End pubsub connections
        await self.pubsub.unlisten(self.uuid_points)
        await self.pubsub.unlisten(self.uuid_bits)
        await self.pubsub.unlisten(self.uuid_subs)
        self.pubsub.stop()

        # Close API
        await self.api.close()

        return

    async def callback_points(self, uuid: UUID, data: dict):
        """Point redeem handler"""
        self.log("callback_points",json.dumps(data))

        # Validate user provided text
        if hasattr(data['data']['redemption'], 'user_input'):
            text=data['data']['redemption']['user_input']
        else:
            text=""

        # Send data to receivers
        self.emit_interact(data['data']['redemption']['user']['display_name'],
                            data['data']['redemption']['reward']['title'],
                            text
                            )
        return


    async def callback_bits(self, uuid: UUID, data: dict):
        """Bit cheer handler"""
        self.log("callback_bits",json.dumps(data))

        # Send data to receivers
        self.emit_donate(data['data']['user_name'],
                            str(data['data']['bits_used'])+"b",
                            data['data']['chat_message']
                            )
        return


    async def callback_subs(self, uuid: UUID, data: dict):
        """Subscription handler"""
        self.log("callback_subs",json.dumps(data))

        # Get plain english version of sub level
        sub_type=""
        if (str(data['sub_plan']) == "1000"):
            sub_type="tier one"
        if (str(data['sub_plan']) == "2000"):
            sub_type="tier two"
        if (str(data['sub_plan']) == "3000"):
            sub_type="tier three"
        if (str(data['sub_plan']) == "Prime"):
            sub_type="prime"

        # Determine length of sub
        sub_len=""
        if ('benefit_end_month' in data and data['benefit_end_month'] != 0):
            sub_len="for "+str(int(data['benefit_end_month'])+1)+" months"
        if ('multi_month_duration' in data and data['multi_month_duration'] > 1):
            sub_len="for "+str(data['multi_month_duration'])+" months"

        # Sub type and build output message
        line=""
        if str(data['context']) ==  "subgift":
            line=str(data['display_name'])
            line += " gave a "+sub_type+" gift sub "+sub_len+" to "+str(data['recipient_display_name'])
        elif str(data['context']) ==  "anonsubgift" or str(data['context']) ==  "anonresubgift":
            line += "Anonymous gifter gave a "+sub_type+" gift sub "+sub_len+" to "+str(data['recipient_display_name'])
        else:
            line=str(data['display_name'])
            line += " subbed as "+sub_type+" "+sub_len+" and says "+str(data['sub_message']['message'])

        # Send data to receivers
        self.emit_donate(data['user_name'],
                            str(data['sub_plan'])+"s",
                            line
                            )
        return

