from scraper.kalibrr import LISTING_URL, fetch_html, extract_jobs, to_job_in
from scraper.client import send_job

def main():
    html = fetch_html(LISTING_URL)
    jobs = extract_jobs(html)
    for job in jobs:
        result = to_job_in(job)
        response = send_job(result)
        print(response.status_code, response.json())
        
if __name__ == "__main__":
    main()