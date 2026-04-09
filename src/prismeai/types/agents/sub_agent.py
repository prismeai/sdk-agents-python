from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SubAgentConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    agent_id: str
    name: Optional[str] = None
    description: Optional[str] = None
