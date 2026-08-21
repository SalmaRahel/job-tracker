from ..database import Base
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.models import User

class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)

    certifications_json: Mapped[dict | None] = mapped_column(JSON)
    projects_json: Mapped[dict | None] = mapped_column(JSON)
    experience_json: Mapped[dict | None] = mapped_column(JSON)
    education_json: Mapped[dict | None] = mapped_column(JSON)
    links_json: Mapped[dict | None] = mapped_column(JSON)
    languages_json: Mapped[dict | None] = mapped_column(JSON)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="profile")
    skills: Mapped[list["Skill"]] = relationship("Skill", back_populates="profile")

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"))
    profile: Mapped["Profile"] = relationship("Profile", back_populates="skills")