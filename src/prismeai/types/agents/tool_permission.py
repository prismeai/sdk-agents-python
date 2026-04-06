from __future__ import annotations
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

class Approver(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str
    id: Optional[str] = None

class ToolRule(BaseModel):
    model_config = ConfigDict(extra="allow")
    tool: str
    policy: str
    conditions: Optional[dict[str, Any]] = None
    approvers: Optional[List[Approver]] = None

class ToolPermissions(BaseModel):
    model_config = ConfigDict(extra="allow")
    default: str
    tools: Optional[List[ToolRule]] = None
