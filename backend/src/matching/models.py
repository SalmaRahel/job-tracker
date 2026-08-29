from ..database import Base
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..jobs.models import Job

class MatchResult(Base):
    __tablename__ = "matchresult"

    id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column()
    missing_requirements: Mapped[list[str]] = mapped_column(JSON)#should we use list[str] or dict
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), unique=True)
    job: Mapped["Job"] = relationship("Job", back_populates="matchresult")