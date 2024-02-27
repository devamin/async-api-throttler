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
            self._count_down = CountDown(
                                    interval=(period*60/max_calls), 
                                    maximum=max_calls
                                )

    @property
    def locked(self) -> bool:
        return not self._count_down.free_room if self._count_down else False
    
    async def consume(self):
        if self.locked:
            logger.warn("Api Throttler reached limit")
        if self._count_down:
            await self._count_down.wait_increment()
        if self._parent_throttler:
            await self._parent_throttler.consume()
        
    def limits(self, calls:int, period:int):
        func_throttler = AsyncApiThrottler(max_calls=calls, period=period, parent_throttler=self)
        def limits_wrapper(func):
            @wraps(func)
            async def wrapper(*args, **kargs):
                await func_throttler.consume()
                return await func(*args, **kargs)
            return wrapper
        return limits_wrapper
