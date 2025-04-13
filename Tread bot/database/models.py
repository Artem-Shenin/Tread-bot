from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, MetaData, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .engine_core import Base  # Changed to relative import
import enum

class ThreadType(enum.Enum):
    ANNOUNCEMENT = "объявления"
    DISCUSSION = "обсуждение"
    UNKNOWN = "неизвестный"

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)

class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    
    # Отношение один-ко-многим с тредами
    threads: Mapped[list["Thread"]] = relationship("Thread", back_populates="group", cascade="all, delete-orphan")

class Thread(Base):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(String, nullable=False)
    thread_type: Mapped[str] = mapped_column(String, nullable=False, default=ThreadType.UNKNOWN.value)
    
    # Внешний ключ для связи с группой
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    
    # Отношение многие-к-одному с группой
    group: Mapped["Group"] = relationship("Group", back_populates="threads")
    
    # Составной уникальный индекс для thread_id и group_id
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
