from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AnalyticsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    conversations: Optional[int] = None
    messages: Optional[int] = None
    unique_users: Optional[int] = None
