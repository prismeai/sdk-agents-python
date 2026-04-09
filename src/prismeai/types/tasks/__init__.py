from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Task(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
