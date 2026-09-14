from scraper.kalibrr import LISTING_URL, fetch_listing, extract_jobs, to_job_in
from scraper.client import send_job

def main():
    data = fetch_listing(LISTING_URL)
    jobs = extract_jobs(data)
    for job in jobs:
        result = to_job_in(job)
        response = send_job(result)
        print(response.status_code, response.json())
        
if __name__ == "__main__":
    main()