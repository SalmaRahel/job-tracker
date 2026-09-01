from ..database import Base
from sqlalchemy import String, ForeignKey, func, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import TSVECTOR


if TYPE_CHECKING:
    from ..jobs.models import Job


class CVGeneration(Base):
    __tablename__ = "cv_generations"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), unique=True)
    job: Mapped["Job"] = relationship("Job", back_populates="cvgeneration")
    s3_key: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
