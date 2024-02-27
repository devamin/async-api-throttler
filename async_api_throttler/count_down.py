import asyncio

from async_api_throttler.exceptions import CounterReachedMaximumError


class CountDown:
    def __init__(self, interval:int = 1, initial_value:int=0, minimum:int=0, maximum:int=float('inf')):
        assert interval > 0
        self._value = initial_value
        self._min = minimum
        self._max = maximum
        self._interval=interval
        self._count_down_task = asyncio.create_task(self._count_down())
        self._waiters = asyncio.Queue()
        
    def __del__(self):
        self._count_down_task.cancel()
        
    @property
    def free_room(self):
        return self._value < self._max
        
    @property
    def value(self):
        return self._value
    
    def increment(self):
        if self._value < self._max:
            self._value +=1
        else:
            raise CounterReachedMaximumError
        
    async def wait_increment(self):
        try:
            self.increment()
        except CounterReachedMaximumError:
            wait_event = asyncio.Event()
            self._waiters.put_nowait(wait_event)
            await wait_event.wait()
            self.increment()
         
    def _decrement(self):
        if self._value > self._min:
            self._value-=1
        if not self._waiters.empty():
            self._waiters.get_nowait().set()
        
    async def _count_down(self):
        while True:
            self._decrement()
            await asyncio.sleep(self._interval)

