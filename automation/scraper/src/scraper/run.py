import argparse

from scraper.client import send_job
from scraper.kalibrr import LISTING_URL, extract_jobs, fetch_listing, to_job_in


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve WFH Jobs list from Kalibrr and send it to jobradar"
        )
    parser.add_argument("--dry-run", action="store_true",
                        help="fetch and map jobs from Kalibrr, "
                        "print them instead of sending to jobradar")
    args = parser.parse_args()

    data = fetch_listing(LISTING_URL)
    jobs = extract_jobs(data)
    for job in jobs:
        result = to_job_in(job)
        if args.dry_run:
            print(result)
        else:
            response = send_job(result)
            print(response.status_code, response.json())

        
if __name__ == "__main__":
    main()