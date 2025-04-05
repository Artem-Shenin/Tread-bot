from sqlalchemy import Table, Column, Integer, BigInteger, String, ForeignKey, MetaData
from sqlalchemy.orm import Mapped, mapped_column
from engine import Base


class Admins(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, unique=True)  