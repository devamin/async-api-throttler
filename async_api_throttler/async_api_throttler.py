import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from functools import wraps
import logging
from typing import Optional
from async_api_throttler.count_down import CountDown

logger = logging.getLogger(__name__)

class AsyncApiThrottler:
    
    def __init__(self, 
                 max_calls:Optional[int] = None, 
                 period:Optional[int] = None,
                 parent_throttler:Optional["AsyncApiThrottler"]=None,
                 ):
        self._max_calls = max_calls
        self._period = period
        self._parent_throttler:AsyncApiThrottler = parent_throttler
        self._count_down:Optional[CountDown] = None
        if self._max_calls is not None and self._period is not None:
            #Breathingroom
            self._max_calls =self._max_calls-1 if self._max_call > 1 else self._max_calls
            self._count_down = CountDown(
                                    interval=(period*60)/self._max_calls, 
                                    maximum=max_calls
                                )

    @property
    def locked(self) -> bool:
        locked = not self._count_down.free_room if self._count_down else False
        locked = locked or self._parent_throttler.locked if self._parent_throttler else locked
        return locked
    
    @asynccontextmanager
    async def consume(self):
        contexts = []
        if self.locked:
            logger.warning("Api Throttler reached limit")
        if self._count_down:
            contexts.append(self._count_down.wait_increment())
        if self._parent_throttler:
            contexts.append(self._parent_throttler.consume())
        if contexts:
            async with AsyncExitStack() as stack:
                await asyncio.gather(*[stack.enter_async_context(ctx) for ctx in contexts])
                yield
        else:
            yield
            
            
    def limits(self, calls: Optional[int] = None, period:Optional[int] = None):
        if calls and period:
            func_throttler = AsyncApiThrottler(max_calls=calls, period=period, parent_throttler=self)
        else:
            func_throttler = self
        def limits_wrapper(func):
            @wraps(func)
            async def wrapper(*args, **kargs):
                async with func_throttler.consume():
                    res = await func(*args, **kargs)
                return res
            return wrapper
        return limits_wrapper
