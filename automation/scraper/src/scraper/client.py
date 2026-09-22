import sys
import time

import httpx


def send_job(data: dict):
    for atmp in range(1,6):
        try:
            response = httpx.post("http://127.0.0.1:8000/jobs", json=data)
            return response
        except httpx.ConnectError:
            if atmp==5:
                raise
            else:
                delay = 2**atmp
                print(f"Attempt no {atmp} | sleep {delay}",file=sys.stderr)
                time.sleep(delay)
