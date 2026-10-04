from typing import Annotated

from pydantic import BaseModel, StringConstraints


class AskRequest(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class AskResponse(BaseModel):
    answer: str
    row_count: int
