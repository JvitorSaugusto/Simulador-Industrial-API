from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from enums.factory_enums import DownTimeEventTypeEnum, DownTimeSeverityEnum


class DownTimeEventModel(Base):
    __tablename__= "down_time_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    type: Mapped[DownTimeEventTypeEnum] = mapped_column(SQLEnum(DownTimeEventTypeEnum), nullable=False)
    severity: Mapped[DownTimeSeverityEnum] = mapped_column(SQLEnum(DownTimeSeverityEnum), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    duration: Mapped[float] = mapped_column()