import asyncio
from contextlib import AsyncExitStack, ExitStack
from time import perf_counter
import pytest

from async_api_throttler.count_down import CountDown
from async_api_throttler.exceptions import CounterReachedMaximumError

@pytest.mark.asyncio 
async def test_trigger_counter_reached_maximum():
    cd = CountDown(interval=0.1, maximum=2)
    with ExitStack() as stack:
        stack.enter_context(cd.increment())
        stack.enter_context(cd.increment())
        with pytest.raises(CounterReachedMaximumError) as exc_info:
            stack.enter_context(cd.increment())
    
@pytest.mark.asyncio
async def test_count_down_minimum():
    cd = CountDown(interval=0.01, maximum=1)
    with cd.increment():
        assert cd.value == 1
    await asyncio.sleep(0.03)
    assert cd.value == 0

