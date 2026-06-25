from enum import Enum


class LineStatusEnum(str, Enum):
    IDLE = "idle"
    STOP = "stop"
    MAINTENANCE = "maintenance"
    PRODUCTION = "production"
    
class ProductionOrderEnum(str, Enum):
    STOP = "stop"
    FINISHED = "finished"
    PENDING = "pending"
    PRODUCTION = "production"