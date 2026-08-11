from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from enums.factory_enums import ProductionOrderEnum


if TYPE_CHECKING:
    from models.production_line_model import ProductionLineModel
    from models.oee_model import OeeRecordModel
    
class ProductionOrderModel(Base):
    __tablename__= "production_orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_planned: Mapped[int] = mapped_column()
    quantity_produced: Mapped[int] = mapped_column(default=0)
    quantity_good: Mapped[int] = mapped_column(default=0)
    quantity_bad: Mapped[int] = mapped_column(default=0)
    status: Mapped[ProductionOrderEnum] = mapped_column(SQLEnum(ProductionOrderEnum), default=ProductionOrderEnum.PENDING, nullable=False)
    planned_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    planned_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id", ondelete="CASCADE"))
    production_line: Mapped["ProductionLineModel"] = relationship("ProductionLineModel", back_populates="production_orders")
    oee_records: Mapped[List["OeeRecordModel"]] = relationship("OeeRecordModel", back_populates="production_order") 