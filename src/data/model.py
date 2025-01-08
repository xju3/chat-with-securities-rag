from sqlalchemy import ForeignKey
from sqlalchemy import String, Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime
from sqlalchemy import String
from dataclasses import dataclass, asdict
import types
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass


@dataclass
class SecMa(Base):
    __tablename__ = "sec_ma"
    code: Mapped[str] = mapped_column(primary_key=True, type_= String(12))
    ma5: Mapped[float] = mapped_column()
    ma10: Mapped[float] = mapped_column()
    ma15: Mapped[float] = mapped_column()
    ma20: Mapped[float] = mapped_column()
    ma30: Mapped[float] = mapped_column()
    ma60: Mapped[float] = mapped_column()
    
@dataclass
class SecInfo(Base):
    __tablename__ = "sec_info"
    code: Mapped[str] = mapped_column(primary_key=True, type_= String(12))
    name: Mapped[str] = mapped_column(String(32))
    def __repr__(self) -> str:
        return f"SecInfo(code={self.code!r}, name={self.name!r})"

@dataclass
class TransItem(Base):
    __tablename__ = "trans_item"
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    code: Mapped[str] = mapped_column()
    date : Mapped[datetime] = mapped_column()
    open : Mapped[float] = mapped_column()

    close : Mapped[float] = mapped_column()
    high : Mapped[float] = mapped_column()
    low : Mapped[float] = mapped_column()

    qty : Mapped[float] = mapped_column()
    amt : Mapped[float] = mapped_column()
    fluc : Mapped[float] = mapped_column()

    pct: Mapped[float] = mapped_column()
    delta : Mapped[float] = mapped_column()
    rate : Mapped[float] = mapped_column()
