from decimal import Decimal
from typing import List
from sqlalchemy import Enum as SQLEnum, String, Integer, Text, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from enums.factory_enums import LineStatusEnum
from models.machine_model import MachineModel
from models.production_order_model import ProductionOrderModel


class ProductionLineModel(Base):
    __tablename__= "production_lines"
    
    id: Mapped [int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped [str]  = mapped_column(String(250), nullable=False)
    description: Mapped [str | None] = mapped_column(Text)
    target_oee: Mapped [Decimal]  = mapped_column(Numeric(5, 2), default=Decimal("85.00"))
    ideal_production_rate: Mapped [float]  = mapped_column(Float)
    current_production_rate: Mapped [float]  = mapped_column(Float, default=0.0)
    production_rate: Mapped [float]  = mapped_column(Float, default=0.0)
    total_runtime_minutes: Mapped [int]  = mapped_column(Integer)
    machines: Mapped[List[MachineModel | None]] = relationship(back_populates="production_line")
    production_orders: Mapped[List[ProductionOrderModel | None]] = relationship(back_populates="production_line")
    simulation_status: Mapped[LineStatusEnum] = mapped_column(SQLEnum(LineStatusEnum), default=LineStatusEnum.IDLE, nullable=False)
