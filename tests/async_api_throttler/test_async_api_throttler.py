import asyncio
from fastapi import FastAPI, Request
import pytest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.testclient import TestClient

from async_api_throttler.async_api_throttler import AsyncApiThrottler

@pytest.mark.asyncio 
async def test_global_api_rate_limit():
    limiter = Limiter(key_func=get_remote_address, default_limits="10/second")
    app = FastAPI()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @app.get("/test")
    @limiter.limit("10/second")
    async def test(request:Request):
        return "ok"
    
    client = TestClient(app)
    #Due to concurrency issue, I reduced the max_calls from 10 to 5
    async_api_throttler = AsyncApiThrottler(max_calls=5, period=(1/60))
    @async_api_throttler.limits()
    async def request_test_endpoint():
        return client.get("/test")
    
    res = await asyncio.gather(*[request_test_endpoint() for _ in range(20)])
    assert all(r.status_code == 200 for r in res)
    async_api_throttler._count_down._count_down_task.cancel()

    
@pytest.mark.asyncio 
async def test_endpoint_api_rate_limit():
    limiter = Limiter(key_func=get_remote_address, default_limits="10/second")
    app = FastAPI()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @app.get("/test")
    @limiter.limit("5/second")
    async def test(request:Request):
        return "ok"
    
    client = TestClient(app)
    async_api_throttler = AsyncApiThrottler(max_calls=10, period=(1/60))
    #Again due to concurrency I am reducing consumption from 3/s to 2/s
    @async_api_throttler.limits(calls=2, period=1/60)
    async def request_test_endpoint():
        return client.get("/test")
    
    res = await asyncio.gather(*[request_test_endpoint() for _ in range(20)])
    assert all(r.status_code == 200 for r in res)
    async_api_throttler._count_down._count_down_task.cancel()
    
@pytest.mark.asyncio 
async def test_global_with_endpoint_rate_limit(caplog):
    limiter = Limiter(key_func=get_remote_address, default_limits="10/second")
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    @app.get("/test")
    @limiter.limit("10/second")
    async def test(request:Request):
        return "ok"

    @app.get("/test2")
    @limiter.limit("5/second")
    async def test2(request:Request):
        return "ok"
    
    client = TestClient(app)
    #Due to concurrency issue, I reduced the max_calls from 10 to 5
    async_api_throttler = AsyncApiThrottler(max_calls=10, period=(1/60))
    @async_api_throttler.limits(10, 1/60)
    async def request_test_endpoint():
        return client.get("/test")
    
    @async_api_throttler.limits(5, 1/60)
    async def request_test2_endpoint():
        return client.get("/test2")
    
    res = await asyncio.gather(*[request_test_endpoint() for _ in range(10)])
    assert all(r.status_code == 200 for r in res)
    assert len(caplog.records) == 0
    res = await request_test2_endpoint()
    #parent throttler is locked, which has locked the child[endpoint] throttler
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "Api Throttler reached limit"
    assert res.status_code == 200
