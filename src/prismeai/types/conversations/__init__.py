from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Conversation(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    agent_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None

class ConversationCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    agent_id: Optional[str] = None
    name: Optional[str] = None

class ConversationUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None

class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    role: str
    content: str
    created_at: Optional[str] = None
