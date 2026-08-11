from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.production_order_model import ProductionOrderModel

class OeeRecordModel(Base):
    __tablename__="oee_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id", ondelete="CASCADE"))
    production_order: Mapped["ProductionOrderModel"] = relationship("ProductionOrderModel", back_populates="oee_records") 
    availability: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    performance: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    quality: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    oee: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))