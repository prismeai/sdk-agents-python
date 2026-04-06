from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class Skill(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None

class SkillCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None

class SkillUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None
    description: Optional[str] = None
