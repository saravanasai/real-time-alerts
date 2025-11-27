from enum import Enum
from pydantic import BaseModel
from typing import List


class MetalType(str, Enum):
    gold = 'gold'
    silver = 'silver'


class Alert(BaseModel):
    user_id: int
    alert_price: int
    metal_type: MetalType


class AlertResponseFormatter(BaseModel):
    data: Alert
