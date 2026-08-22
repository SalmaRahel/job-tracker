from ..database import Base
from sqlalchemy import String, Text, Date, Enum, ForeignKey, func, DateTime, Computed, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date, datetime
import enum
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import TSVECTOR


if TYPE_CHECKING:
    from ..auth.models import User

class ApplicationStatus(enum.Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    ONLINE_ASSESSMENT = "Online Assessment"
    INTERVIEW = "Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class Job(Base):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    company_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(150))
    location: Mapped[str] = mapped_column(String(50))
    job_description: Mapped[str] = mapped_column(Text())
    application_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    job_link: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    search_vector: Mapped[Optional[str]] = mapped_column(
    TSVECTOR,
    Computed("to_tsvector('english', company_name || ' ' || position || ' ' || job_description)"),
    nullable=True
)  


