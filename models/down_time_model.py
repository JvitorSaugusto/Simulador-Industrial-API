from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from enums.factory_enums import DownTimeEventTypeEnum, DownTimeSeverityEnum, DownTimeEventStatusEnum


class DownTimeEventModel(Base):
    __tablename__= "down_time_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"))
    production_order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    type: Mapped[DownTimeEventTypeEnum] = mapped_column(SQLEnum(DownTimeEventTypeEnum), nullable=False)
    severity: Mapped[DownTimeSeverityEnum | None] = mapped_column(SQLEnum(DownTimeSeverityEnum), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[DownTimeEventStatusEnum] = mapped_column(SQLEnum(DownTimeEventStatusEnum), default=DownTimeEventStatusEnum.OPEN)
    duration: Mapped[float] = mapped_column(Float)
