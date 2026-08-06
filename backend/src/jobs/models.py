from ..database import Base
from sqlalchemy import String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date
import enum
from typing import TYPE_CHECKING

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
    company_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(150))
    location: Mapped[str] = mapped_column(String(50))
    application_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    job_link: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="jobs")




