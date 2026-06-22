from decimal import Decimal
from sqlalchemy import String, Integer, Text, Numeric, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from enums.production_line_enums import LineStatusEnum


class ProductionLineModel(Base):
    __tablename__= "production_lines"
    
    id: Mapped [int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped [str]  = mapped_column(String(250), nullable=False)
    description: Mapped [str | None] = mapped_column(Text)
    target_oee: Mapped [Decimal]  = mapped_column(Numeric(5, 2), default=Decimal("85.00"))
    ideal_production_rate: Mapped [float]  = mapped_column(Float)
    current_production_rate: Mapped [float]  = mapped_column(Float)
    production_rate: Mapped [float]  = mapped_column(Float)
    total_runtime_minutes: Mapped [int]  = mapped_column(Integer)
    status: Mapped[LineStatusEnum] = mapped_column(SQLEnum(LineStatusEnum), default=LineStatusEnum.IDLE, nullable=False)