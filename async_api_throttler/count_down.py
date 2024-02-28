import asyncio
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
import time

from async_api_throttler.exceptions import CounterReachedMaximumError


class CountDown:
    def __init__(self, interval:float = 1.0, initial_value:int=0, minimum:int=0, maximum:int=float('inf')):
        assert interval > 0
        self._value = initial_value
        self._min = minimum
        self._max = maximum
        self._interval=interval
        self._count_down_task = asyncio.create_task(self._count_down())
        self._waiters = asyncio.Queue()
        self._start_time:float = 0.0
        self._max_time:float = 0.0
        
    def __del__(self):
        try:
            self._count_down_task.cancel()
        except RuntimeError:
            pass
        
    def __str__(self):
        return f"CountDown; free_room:{self.free_room}, value:{self._value}, max:{self._max}, interval:{self._interval}, waiters:{self._waiters.qsize()}"
    
    @property
    def free_room(self):
        return self._value < self._max
        
    @property
    def value(self):
        return self._value
    
    @contextmanager
    def increment(self):
        if self._value < self._max:
            p_value = self._value
            self._value +=1
            yield 
            if p_value == 0:
                self._start_time = time.time()
            if self._value == self._max:
                self._max_time = time.time()
        else:
            raise CounterReachedMaximumError
    
    @asynccontextmanager   
    async def wait_increment(self):
        try:
            with self.increment():
                yield
        except CounterReachedMaximumError:
            wait_event = asyncio.Event()
            self._waiters.put_nowait(wait_event)
            await wait_event.wait()
            with self.increment():
                yield

    def _decrement(self):
        if self._value > self._min:
            self._value-=1
        if not self._waiters.empty():
            self._waiters.get_nowait().set()
        
    async def _count_down(self):
        while True:
            await asyncio.sleep(self._interval)
            if self._value == self._max:
                if self._max_time and self._start_time:
                    elapsed_time = self._max_time - self._start_time
                    if elapsed_time < self._interval*self._max:
                        await asyncio.sleep(self._interval*self._max - elapsed_time)
                else:
                    continue
            self._decrement()

