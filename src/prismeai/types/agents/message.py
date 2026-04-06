from __future__ import annotations
from typing import Any, Optional, List
from pydantic import BaseModel, ConfigDict

class MessagePart(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str
    text: Optional[str] = None
    url: Optional[str] = None
    mime_type: Optional[str] = None
    data: Optional[str] = None

class MessageSend(BaseModel):
    model_config = ConfigDict(extra="allow")
    text: Optional[str] = None
    parts: Optional[List[MessagePart]] = None
    conversation_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None

class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    output: Optional[str] = None
    conversation_id: Optional[str] = None
    task_id: Optional[str] = None

class SSEEvent(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str
    text: Optional[str] = None
    task_id: Optional[str] = None
    status: Optional[str] = None
    output: Optional[str] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None
