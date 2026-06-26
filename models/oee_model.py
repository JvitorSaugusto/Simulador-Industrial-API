from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class OeeRecordModel(Base):
    __tablename__="oee_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(ForeignKey("production_order.id", ondelete="CASCADE"))
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_line.id", ondelete="CASCADE"))
    availability: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    perfomance: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    quality: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    oee: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    start_period: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_period: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))