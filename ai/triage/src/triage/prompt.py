from triage.schemas import Posting


def render(posting: Posting) -> str:
    if posting.is_remote is None:
        wfh = "Work from home: not stated by the job board"
    elif posting.is_remote is True:
        wfh = "Work from home: yes, according to the job board"
    else:
        wfh = "Work from home: no, according to the job board"
    lines = [f"Title: {posting.title}"]
    if posting.company is not None:
        lines.append(f"Company: {posting.company}")
    if posting.location is not None:
        lines.append(f"Location: {posting.location}")
    lines.append(wfh)
    lines.append(f"URL: {posting.url}")
    return "\n".join(lines)
