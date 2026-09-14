import httpx

LISTING_URL = "https://www.kalibrr.id/kjs/job_board/search"

def fetch_listing(url):
    response = httpx.get(url, params={"limit": 200, "offset": 0, "is_work_from_home": "true"}, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.json()
    
def extract_jobs(data: dict):
    if data["from_alternative"]:
        raise ValueError("Server return alternative value")
    if len(data["jobs"]) != data['count']:
        raise ValueError(f"Length job: {len(data['jobs'])} count: {data['count']}")
    else:
        return data['jobs']

def to_job_in(raw):
    components = raw.get("google_location", {}).get("address_components", {})
    parts = [components.get("city"), components.get("region"), components.get("country")]
    filled = [x for x in parts if x]
    location = ", ".join(filled) or None
    data = {"source": "kalibrr",
            "ext_id": str(raw["id"]),
            "title": raw["name"],
            "company": raw["company_name"],
            "posted_at": raw["activation_date"],
            "description": raw["description"],
            "url": f"https://www.kalibrr.id/id-ID/c/{raw['company']['code']}/jobs/{raw['id']}/{raw['slug']}",
            "location": location
    }
    return data

def main():
    listing = fetch_listing(LISTING_URL)
    jobs = extract_jobs(listing)
    for job in jobs:
        result = to_job_in(job)
        print(result)
    
if __name__ == "__main__":
    main()