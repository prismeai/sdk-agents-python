from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class Artifact(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    content: Optional[Any] = None

class ArtifactUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None
    content: Optional[Any] = None
