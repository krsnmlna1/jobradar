from triage.schemas import Posting


def parse_raw(text: str) -> Posting:
    header, _, body = text.partition("\n\n")
    fields = {}
    for line in header.splitlines():
        key, _, value = line.partition(": ")
        fields[key] = value
    body = body.strip()
    description = body if body != "" else None
    return Posting(title=fields["title"], url=fields["url"], description=description)
