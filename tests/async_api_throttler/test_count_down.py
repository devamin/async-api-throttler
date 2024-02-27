import asyncio
from time import perf_counter
import pytest

from async_api_throttler.count_down import CountDown
from async_api_throttler.exceptions import CounterReachedMaximumError

@pytest.mark.asyncio 
async def test_trigger_counter_reached_maximum():
    cd = CountDown(interval=0.1, maximum=2)
    cd.increment()
    cd.increment()
    with pytest.raises(CounterReachedMaximumError) as exc_info:
        cd.increment()
    cd._count_down_task.cancel()

@pytest.mark.asyncio
async def test_count_waited_time_for_counter_incrementation():
    interval = 0.1
    cd = CountDown(interval=interval, maximum=2)
    start = perf_counter()
    await asyncio.gather(cd.wait_increment(), cd.wait_increment(),cd.wait_increment())
    assert interval == pytest.approx(perf_counter()-start, rel=0.02)
    cd._count_down_task.cancel()
    
@pytest.mark.asyncio
async def test_count_down_minimum():
    cd = CountDown(interval=0.01, maximum=1)
    cd.increment()
    await asyncio.sleep(0.02)
    assert cd.value == 0
    cd._count_down_task.cancel()
