#!/usr/bin/python3
from stream.api_base import APIbase

from twitchAPI.twitch import Twitch
from twitchAPI.pubsub import PubSub
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope
from utils.coalescer import EventCoalescer
from collections import namedtuple

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
        text=str(""+str(data['data']['redemption']['user_input']))

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

    # Mapping of known sub plans to plain-English names
    _sub_types = {
        "1000": "tier one",
        "2000": "tier two",
        "3000": "tier three",
        "Prime": "prime"
    }

    def _get_sub_type(self, sub_plan: str):
        """Returns a plain-English version of sub plan level if available."""

        return APItwitch._sub_types.get(sub_plan, "")

    async def callback_subs(self, uuid: UUID, data: dict):
        """Subscription handler"""
        self.log("callback_subs",json.dumps(data))

        # Determine length of sub
        sub_months=1

        if ('benefit_end_month' in data and data['benefit_end_month'] != 0):
            sub_months = int(data['benefit_end_month']) + 1

        if ('multi_month_duration' in data and data['multi_month_duration'] > 1):
            sub_months = int(data['multi_month_duration'])

        # Extract other request fields
        user_name = data['user_name']
        display_name = str(data['display_name'])
        sub_plan = str(data['sub_plan'])
        context = str(data['context'])

        # Gifted subs need to be coalesced before they can be formatted
        if context ==  "subgift":
            self._coalesce_gifted_sub(user_name,
                                      display_name,
                                      sub_plan,
                                      sub_months,
                                      str(data['recipient_display_name']))

        elif context ==  "anonsubgift" or context ==  "anonresubgift":
            self._coalesce_gifted_sub(user_name,
                                      "Anonymous gifter",
                                      sub_plan,
                                      sub_months,
                                      str(data['recipient_display_name']))

        else:
            # ... but a user's own sub will always be a single event so
            # format it here and send it straight through.

            # Find plain-English plan name and sub length
            sub_type = self._get_sub_type(sub_plan)
            sub_len = ""
            if sub_months > 1:
                sub_len = "for " + str(sub_months) + " months"

            line = (display_name + " subbed as " + sub_type + " " + sub_len +
                    " and says " + str(data['sub_message']['message']))

            # Send data to receivers
            self.emit_donate(user_name, sub_plan+"s", line)

        return

    # use a tuple of (user_name, display_name, sub_plan, sub_months) to group
    # gift subs together; make it a named tuple for ease of reading!
    _GiftSubContext = namedtuple('GiftSubContext',
                                 ['user_name',
                                  'display_name',
                                  'sub_plan',
                                  'sub_months'])

    # dict to contain all our coalescers for incoming gift subs, keyed by above
    _giftsub_coalescers = {}

    # time (in seconds) to wait after the last gifted sub before
    # generating a message covering the entire list
    GIFTSUB_COALESCE_TIMEOUT = 2.0

    async def _coalesce_gifted_sub(self,
                                   user_name: str,
                                   display_name: str,
                                   sub_plan: str,
                                   sub_months: int,
                                   recipient: str):
        """Coalesce potentially several gift subs into one event.
        
        Since Twitch delivers (only) individual gift sub events even if a user
        has donated several in one go, we want to group these together into
        one event that we can process as a single message.  This needs to be
        done based on a combination of the donor name, the sub plan and the sub
        length (all of which we include in the message text where applicable),
        with only the recipient names varying in each coalesced event."""

        def _coalescer_callback(context, recipients):
            """Internal callback to unpack context from EventCoalescer."""

            # Unpack the context object and forward events to outer callback
            self.callback_gifted_sub_list(context.user_name,
                                          context.display_name,
                                          context.sub_plan,
                                          context.sub_months,
                                          recipients)

        # Create a context tuple which will be used both as a key into the
        # _giftsub_coalescers dict and as a context object for our internal
        # callback, _coalescer_callback.
        context = self._GiftSubContext(user_name,
                                       display_name,
                                       sub_plan,
                                       sub_months)

        if context in self._giftsub_coalescers:
            # We already have a coalescer for this event, so we can just add it
            self._giftsub_coalescers[context].add_event(recipient)

        else:
            # We don't yet have a coalescer for this event, so create a new one
            # and add the new (first) event to it
            coalescer = EventCoalescer(self.GIFTSUB_COALESCE_TIMEOUT,
                                       context,
                                       _coalescer_callback)

            self._giftsub_coalescers[context] = coalescer
            coalescer.add_event(recipient)

    async def callback_gifted_sub_list(self,
                                       user_name: str,
                                       display_name: str,
                                       sub_plan: str,
                                       sub_months: int,
                                       recipients: list):
        """Gifted sub handler, for potentially multiple recipients."""

        # Find plain-English version of sub plan, number of recipients and
        # length of gifted sub if not a single month.
        sub_len = ""
        sub_type = self._get_sub_type(sub_plan)
        gift_count = len(recipients)
        if sub_months > 1:
            sub_len = "for " + str(sub_months) + " months"

        # Format appropriately as a single gift or a list of names.
        line = ""
        if gift_count == 1:
            line = (display_name + " gave a " + sub_type + " gift sub " +
                    sub_len + " to " + recipients[0])
        else:
            recipients[-1] = "and " + recipients[-1]
            line = (display_name + " gave " + str(gift_count) + " " + sub_type +
                    " gift subs " + sub_len + " to " + ", ".join(recipients))

        # Send data to receivers
        self.emit_donate(user_name, sub_plan+"s", line)
