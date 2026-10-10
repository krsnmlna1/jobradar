from triage.schemas import Posting


def render(posting: Posting) -> str:
    if posting.is_remote is None:
        return "Work from home: not stated by the job board"
    elif posting.is_remote is True:
        return "Work from home: yes, according to the job board"
    else:
        return "Work from home: no, according to the job board"
