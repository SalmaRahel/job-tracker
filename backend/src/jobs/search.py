from sqlalchemy import and_, func, or_
from .models import Job

MAX_TERMS = 8


def escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\%").replace("_", "\_")


def search_filter(text: str):
    text = text.replace("\x00", "")
    terms = text.split()[:MAX_TERMS]
    if not terms:
        return None
    whole_words = Job.search_vector.op("@@")(func.websearch_to_tsquery("english", text))
    partial = and_(*[
        or_(*[
            column.ilike(f"%{escape_like(term)}%", escape="\\")
            for column in (Job.company_name, Job.position, Job.location)
        ])
        for term in terms
    ])
    return or_(whole_words, partial)
