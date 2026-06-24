import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.models.chat import FriendshipStatus

class UserPublic(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class FriendshipBase(BaseModel):
    addressee_id: uuid.UUID

class FriendshipCreate(FriendshipBase):
    pass

class FriendshipResponse(BaseModel):
    id: uuid.UUID
    requester_id: uuid.UUID
    addressee_id: uuid.UUID
    status: FriendshipStatus
    created_at: datetime
    requester: Optional[UserPublic] = None
    addressee: Optional[UserPublic] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class FriendshipStatusUpdate(BaseModel):
    status: FriendshipStatus

class ChatMessageBase(BaseModel):
    receiver_id: uuid.UUID
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    is_read: bool
    deleted_for_everyone: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatMessageDeleteRequest(BaseModel):
    message_ids: List[uuid.UUID]
    delete_type: str # 'everyone' or 'me'

class ChatMessageReadRequest(BaseModel):
    message_ids: List[uuid.UUID]
