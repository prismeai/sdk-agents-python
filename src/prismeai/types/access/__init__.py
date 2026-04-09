from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AccessEntry(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    role: str
    email: Optional[str] = None

class AccessGrant(BaseModel):
    model_config = ConfigDict(extra="allow")
    role: str
    email: Optional[str] = None

class AccessRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    user_id: str
    status: str
