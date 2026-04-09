from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Tool(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None
    type: Optional[str] = None

class ToolCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None
