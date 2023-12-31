from utils.restartable_timeout import RestartableTimeout

class EventCoalescer(RestartableTimeout):
    """Gather together individual events until a specified period of inactivity.
    
    This class maintains a list of incoming event objects, and then fires
    a callback once no new items have been added within a configurable
    timeout period.  The callback is passed a context object, to allow for
    multiple EventCoalescers to share one callback, along with a list of
    the individual event items that have been added since the callback was
    last triggered."""

    def __init__(self, timeout, context, callback):
        """Construct a new EventCoalescer with context and timeout.
        
        Parameters:
            timeout     inactivity timeout, in seconds
            context     an arbitrary object, passed to the callback when fired
            callback    callback to fire when the timeout expires
        """
        RestartableTimeout.__init__(self, timeout, self._inner_callback)
        self._list_callback = callback
        self._context = context
        self._list = []

    async def _inner_callback(self):
        """Called by RestartableTimeout after the inactivity timer expires."""

        # Take a copy of the current list of events and then clear it, so that
        # we don't end up losing any events if the callback causes any new ones
        # to be added!
        events = self._list
        self._list = []

        # Fire our own callback, passing our context and list of new events
        if len(events) > 0:
            await self._list_callback(self._context, events)

    def add_event(self, event):
        """Add an event to the list that will eventually be reported."""
        self._list.append(event)
        self.restart()
