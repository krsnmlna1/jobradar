from scraper.client import send_job
from scraper.kalibrr import LISTING_URL, extract_jobs, fetch_listing, to_job_in


def main():
    data = fetch_listing(LISTING_URL)
    jobs = extract_jobs(data)
    for job in jobs:
        result = to_job_in(job)
        response = send_job(result)
        print(response.status_code, response.json())
        
if __name__ == "__main__":
    main()