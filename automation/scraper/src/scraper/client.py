import httpx
import time

def send_job(data: dict):
    for atmp in range(1,6):
        try:
            response = httpx.post("http://127.0.0.1:8000/jobs", json=data)
            return response
        except httpx.ConnectError:
            if atmp==5:
                raise
            else:
                time.sleep(2**atmp)
    
def main():
    jobs = {"source": "anu.com",
            "ext_id": "test_01",
            "title": "ituanu",
            "company": "PT Anu",
            "url": "http://anu.com"}
    response = send_job(jobs)
    print(response.status_code, response.json())
    
if __name__ == "__main__":
    main()