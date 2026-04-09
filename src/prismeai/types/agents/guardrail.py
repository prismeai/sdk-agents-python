from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class GuardrailConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    type: str
    guardrail_type: str
    config: Optional[dict[str, Any]] = None
    enabled: Optional[bool] = None
