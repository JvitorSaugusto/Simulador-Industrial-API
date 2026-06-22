from enum import Enum


class LineStatusEnum(str, Enum):
    IDLE = "idle"
    STOP = "stop"
    MAINTENANCE = "maintenance"
    PRODUCTION = "production"