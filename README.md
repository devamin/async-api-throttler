
# AsyncApiThrottler README

AsyncApiThrottler is a Python library designed for managing API request rate limits in asynchronous applications. It allows you to easily configure global and endpoint-specific rate limits, ensuring your application adheres to the API's rate limiting policies and prevents being blocked or rate-limited. This README provides a quick start example on how to use AsyncApiThrottler with `httpx` for making asynchronous API requests.

## Quick Start Example

```python
import httpx
from async_api_throttler import AsyncApiThrottler

# Initialize the throttler with a global rate limit
api_throttler = AsyncApiThrottler(max_calls=100, period=1)

# Apply endpoint-specific rate limits using the decorator
@api_throttler.limits(10, 1)
async def request_user_endpoint():
    # Make an asynchronous API request using httpx
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/user')
        return response.json()
```

This example demonstrates how to set up AsyncApiThrottler with a global limit of 100 requests per minute and a specific rate limit of 10 requests per minute for the '/user' endpoint. By integrating AsyncApiThrottler in this way, you ensure your application respects the API's rate limits, promoting efficient and responsible usage of resources.
