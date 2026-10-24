import requests
from time import time
from livekit.agents import function_tool

def check_internet_speed():
    test_url = "https://www.google.com/favicon.ico"
    start = time()

    try:
        r = requests.get(test_url, timeout=3)
        latency = time() - start

        if latency < 0.20:
            return "fast"
        elif latency < 0.60:
            return "medium"
        else:
            return "slow"
    except:
        return "offline"

@function_tool
async def net_status_tool():
    status = check_internet_speed()
    return f"🌐 Internet speed: {status}"
