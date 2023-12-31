import asyncio
from utils.coalescer import EventCoalescer

# Some tests to make sure the event coalescer is doing roughly the right thing!
#
# Ideally I'd use a test framework for this but I'm not sure if Shelby has
# a preferred one, so even a simple command-line test is better than nothing.
async def main():
    """Very basic test routine that I should probably use a framework for."""

    print("""Now performing some simple tests of the EventCoalescer class.

The first test should add five items, one every 0.1 seconds, and display them
two seconds after the last item is added.

The second test will start a second afterwards and will add three items, with a
second's delay between each one; again, it should display the results two
seconds after the last item is added.

The tests will be preceded by a five-second pause during which no events should
fire.\n""")

    start_time = asyncio.get_running_loop().time()

    def print_with_time(msg):
        current_time = asyncio.get_running_loop().time()
        delta_time = current_time - start_time

        print(f"{delta_time:0.6f} sec: {msg}")

    async def list_callback(context, items):
        """Test callback"""

        print_with_time(f"Got a list of items in context '{context}': " +
                        ", ".join(items))

    coalescer = EventCoalescer(2, "test", list_callback)

    def add_test_event(n):
        name = f"Event {n+1}"
        print_with_time(f"Adding {name}")
        coalescer.add_event(name)

    await asyncio.sleep(5)

    for n in range(5):
        add_test_event(n)
        await asyncio.sleep(0.1)

    await asyncio.sleep(3)

    for n in range(5, 8):
        add_test_event(n)
        await asyncio.sleep(1)

    await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
