import asyncio

class RestartableTimeout:
    """Simple utility class to implement a restartable async timeout.

    Each instance of this class represents a single timeout, and will fire a
    callback once after a specified interval.  The timeout can be restarted
    at any time, at which point it is rescheduled for the same interval in the
    future; if it has not yet fired the original scheduled callback will be
    cancelled.
    
    Based on Mikhail Gerasimov's example async timer code from 
    https://stackoverflow.com/a/45430833."""

    def __init__(self, timeout, callback):
        """Starts a new async timeout.
        
        Parameters:
            timeout     timeout duration, in seconds
            callback    async routine to call when the timeout expires
        """

        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        """Cancel any outstanding timeout."""

        self._task.cancel()

    def restart(self):
        """Restart (extend) the timeout period.
        
        If the callback has not yet fired, it will be rescheduled to do so
        after the originally-specified timeout interval.  If it has already
        fired, it will fire again after that same timeout."""

        self.cancel()
        self._task = asyncio.ensure_future(self._job())
