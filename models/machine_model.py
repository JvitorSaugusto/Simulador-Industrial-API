from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from database import Base
from enums.factory_enums import MachineStatusEnum

if TYPE_CHECKING:
    from .production_line_model import ProductionLineModel

class MachineModel(Base):
    __tablename__= "machines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    code: Mapped[str] = mapped_column()
    base_failure_rate: Mapped[float] = mapped_column(default=3.0)
    wear_level: Mapped[float] = mapped_column(default=0.0)
    production_line_id: Mapped[int | None] = mapped_column(ForeignKey("production_lines.id", ondelete="CASCADE"))
    production_line: Mapped["ProductionLineModel | None"] = relationship(back_populates="machines")
    last_start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_stop_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_maintenance_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[MachineStatusEnum] = mapped_column(SQLEnum(MachineStatusEnum), default=MachineStatusEnum.IDLE, nullable=False)