import httpx

def send_job(data: dict):
    response = httpx.post("http://127.0.0.1:8000/jobs", json=data)
    return response
    
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