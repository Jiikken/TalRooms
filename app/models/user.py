from datetime import datetime
from enum import IntEnum

from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, func, SmallInteger
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship
from sqlalchemy.testing.schema import mapped_column


class Base(DeclarativeBase):
    pass

class Role(IntEnum):
    USER = 0
    EDITOR = 1
    ADMIN = 2

class Status(IntEnum):
    AVAILABLE = 1
    BOOKED = 0

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[int] = mapped_column(Integer, default=Role.USER)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_login: Mapped[str] = mapped_column(String, default="0", server_default="0")

class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_room: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=Status.AVAILABLE, server_default=str(Status.AVAILABLE.value))
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str] = mapped_column(String(255), nullable=False)
    end_time: Mapped[str] = mapped_column(String(255), nullable=False)

class RoomsBooking(Base):
    __tablename__ = "rooms_booking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    booked_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    requested_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),nullable=False)

    room: Mapped["Rooms"] = relationship("Rooms", lazy="selectin")
