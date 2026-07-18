from database import Base

from sqlalchemy import String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date

import enum

class ApplicationStatus(enum.Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    ONLINE_ASSESSMENT = "Online Assessment"
    INTERVIEW = "Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"

#Mapped is a type hint that tell python and SQLalchemy that this attribute is mapped to a column in database
class Internship(Base):
    __tablename__ = "internship"

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

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text(), nullable=False)
