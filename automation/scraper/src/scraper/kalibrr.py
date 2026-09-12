import httpx
import re
import json

LISTING_URL = "https://www.kalibrr.id/id-ID/home/work_from_home/y"

def fetch_html(url):
    response = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.text
    
def extract_jobs(html):
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if match is None:
        raise ValueError("__NEXT_DATA__ not found, structure page change")
    data = match.group(1)
    result = json.loads(data)
    
    return result["props"]["pageProps"]["jobs"]

def to_job_in(raw):
    components = raw.get("googleLocation", {}).get("addressComponents", {})
    parts = [components.get("city"), components.get("region"), components.get("country")]
    filled = [x for x in parts if x]
    location = ", ".join(filled) or None
    data = {"source": "kalibrr",
            "ext_id": str(raw["id"]),
            "title": raw["name"],
            "company": raw["companyName"],
            "posted_at": raw["activationDate"],
            "description": raw["description"],
            "url": f"https://www.kalibrr.id/id-ID/c/{raw['company']['code']}/jobs/{raw['id']}/{raw['slug']}",
            "location": location
    }
    return data

def main():
    html = fetch_html(LISTING_URL)
    jobs = extract_jobs(html)
    for job in jobs:
        result = to_job_in(job)
        print(result)
    
if __name__ == "__main__":
    main()