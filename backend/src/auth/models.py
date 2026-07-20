from ..database import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship 

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text(), nullable=False)
    internships: Mapped[list["Internship"]] = relationship("Internship", back_populates="user")