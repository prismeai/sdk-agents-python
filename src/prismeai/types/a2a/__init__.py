from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class A2ASend(BaseModel):
    model_config = ConfigDict(extra="allow")
    message: str
    task_id: Optional[str] = None

class A2AResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    task_id: str
    output: Optional[str] = None

class A2ACard(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
