from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base


class UserRole(str, Enum):
    TUTOR = "tutor"
    STUDENT = "student"


class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReminderKind(str, Enum):
    DAY_BEFORE = "day_before"
    HOUR_BEFORE = "hour_before"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    role: Mapped[str] = mapped_column(String(16))
    full_name: Mapped[str] = mapped_column(String(255))
    tutor_code: Mapped[Optional[str]] = mapped_column(
        String(8), unique=True, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    students_links: Mapped[list["TutorStudentLink"]] = relationship(
        "TutorStudentLink",
        foreign_keys="TutorStudentLink.tutor_id",
        cascade="all, delete-orphan",
        back_populates="tutor",
    )
    tutors_links: Mapped[list["TutorStudentLink"]] = relationship(
        "TutorStudentLink",
        foreign_keys="TutorStudentLink.student_id",
        cascade="all, delete-orphan",
        back_populates="student",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} role={self.role} name={self.full_name}>"


class TutorStudentLink(Base):
    __tablename__ = "tutor_student_links"
    __table_args__ = (UniqueConstraint("tutor_id", "student_id", name="uq_tutor_student"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    subject: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tutor: Mapped[User] = relationship(
        "User", foreign_keys=[tutor_id], back_populates="students_links"
    )
    student: Mapped[User] = relationship(
        "User", foreign_keys=[student_id], back_populates="tutors_links"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(120), default="")
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    materials_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    board_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration_min: Mapped[int] = mapped_column(default=60)
    recurrence: Mapped[str] = mapped_column(String(16), default=RecurrenceType.NONE.value)
    series_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tutor: Mapped[User] = relationship("User", foreign_keys=[tutor_id])
    student: Mapped[User] = relationship("User", foreign_keys=[student_id])
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", cascade="all, delete-orphan", back_populates="lesson"
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(16))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    lesson: Mapped[Lesson] = relationship("Lesson", back_populates="reminders")
    user: Mapped[User] = relationship("User")