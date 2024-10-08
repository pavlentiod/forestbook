from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# Schema for input data (creating a subscription)
class SubscriptionInput(BaseModel):
    access: float = Field(..., description="Access level for the subscription")
    end_at: datetime
    user_id: UUID

# Schema for output data (displaying a subscription)
class SubscriptionOutput(BaseModel):
    id: UUID
    access: float
    created_at: datetime
    end_at: datetime
    user_id: UUID

# Schema for endpoints (updating a subscription)
class SubscriptionEndpoint(BaseModel):
    access: float = Field(..., description="Access level for the subscription")
    end_at: datetime
    user_id: UUID
