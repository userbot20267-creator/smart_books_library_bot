"""Points and Transactions Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserPointsSchema(BaseModel):
    """User points response schema"""
    id: int
    user_id: int
    total_points: int
    available_points: int
    used_points: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointsTransactionSchema(BaseModel):
    """Points transaction response schema"""
    id: int
    user_id: int
    transaction_type: str
    amount: int
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
