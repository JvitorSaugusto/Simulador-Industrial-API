from enum import Enum

# LINHAS DE PRODUÇÃO
class MachineStatusEnum(str, Enum):
    IDLE = "idle"
    STOP = "stop"
    MAINTENANCE = "maintenance"
    PRODUCTION = "production"

# OPS
class ProductionOrderEnum(str, Enum):
    STOP = "stop"
    FINISHED = "finished"
    PENDING = "pending"
    PRODUCTION = "production"
    
# EVENTOS DE PARADA
class DownTimeEventTypeEnum(str, Enum):
    FAILURE = "failure"
    PREVENTIVE = "preventive_maintenance"
    INSPECTION = "inspection"
    
class DownTimeSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "mid"
    HIGH = "high"