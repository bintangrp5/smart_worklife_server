import uuid
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import json

from app.database import get_db
from app.core.dependencies import get_current_user_id
from app.core.config import settings
from app.schemas.chat import UserPublic, FriendshipCreate, FriendshipResponse, FriendshipStatusUpdate, ChatMessageCreate, ChatMessageResponse, ChatMessageDeleteRequest, ChatMessageReadRequest
from app.crud import chat as crud_chat
from app.models.chat import FriendshipStatus

router = APIRouter(prefix="/chat", tags=["chat"])

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        # Menyimpan websocket koneksi per user_id
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

def verify_ws_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id = verify_ws_token(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Klien (Flutter) tidak perlu mengirim pesan via WS untuk disimpan ke database,
            # Flutter akan tetap pakai POST /messages, dan kita akan broadcast dari sana.
            # Websocket ini difokuskan sebagai "saluran pendengar" (Receiver) yang ringan.
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/users/search", response_model=List[UserPublic])
async def search_users(q: str, db: AsyncSession = Depends(get_db), current_user_id: uuid.UUID = Depends(get_current_user_id)):
    if len(q) < 3:
        return []
    users = await crud_chat.search_users(db, q)
    return [u for u in users if u.id != current_user_id]

@router.post("/friends/request", response_model=FriendshipResponse)
async def send_friend_request(req: FriendshipCreate, db: AsyncSession = Depends(get_db), current_user_id: uuid.UUID = Depends(get_current_user_id)):
    if req.addressee_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
    
    friendship = await crud_chat.create_friendship_request(db, current_user_id, req.addressee_id)
    return friendship

@router.get("/friends", response_model=List[FriendshipResponse])
async def get_friends(db: AsyncSession = Depends(get_db), current_user_id: uuid.UUID = Depends(get_current_user_id)):
    friendships = await crud_chat.get_friends_list(db, current_user_id)
    
    result = []
    for f in friendships:
        friend_id = f.requester_id if f.addressee_id == current_user_id else f.addressee_id
        messages = await crud_chat.get_messages(db, current_user_id, friend_id)
        
        last_message = None
        last_message_time = None
        unread_count = 0
        
        if messages:
            last_msg = messages[-1]
            last_message = "Anda menghapus pesan ini" if last_msg.deleted_for_everyone else last_msg.content
            last_message_time = last_msg.created_at
            
            unread_count = sum(1 for m in messages if m.receiver_id == current_user_id and not m.is_read and not m.deleted_for_everyone)
            
        f_dict = FriendshipResponse.model_validate(f).model_dump()
        f_dict['last_message'] = last_message
        f_dict['last_message_time'] = last_message_time
        f_dict['unread_count'] = unread_count
        result.append(f_dict)
        
    return result

@router.get("/friends/requests", response_model=List[FriendshipResponse])
async def get_incoming_requests(db: AsyncSession = Depends(get_db), current_user_id: uuid.UUID = Depends(get_current_user_id)):
    requests = await crud_chat.get_friend_requests(db, current_user_id)
    return requests

@router.put("/friends/{friendship_id}", response_model=FriendshipResponse)
async def respond_to_friend_request(
    friendship_id: uuid.UUID, 
    update: FriendshipStatusUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    friendship = await crud_chat.update_friendship_status(db, friendship_id, update.status)
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship request not found")
    return friendship

@router.delete("/friends/{friendship_id}")
async def remove_friend(
    friendship_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    await crud_chat.remove_friendship(db, friendship_id)
    return {"detail": "Friendship removed"}

@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(
    req: ChatMessageCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    msg = await crud_chat.send_message(db, current_user_id, req.receiver_id, req.content)
    
    # Broadcast pesan yang baru dibuat ke penerima secara real-time via WebSocket
    msg_dict = ChatMessageResponse.model_validate(msg).model_dump()
    # Convert datetime to string agar bisa dikonversi ke JSON
    msg_dict['created_at'] = msg_dict['created_at'].isoformat()
    msg_dict['id'] = str(msg_dict['id'])
    msg_dict['sender_id'] = str(msg_dict['sender_id'])
    msg_dict['receiver_id'] = str(msg_dict['receiver_id'])
    
    await manager.send_personal_message(json.dumps(msg_dict), str(req.receiver_id))
    
    return msg

@router.get("/messages/{other_user_id}", response_model=List[ChatMessageResponse])
async def get_messages(
    other_user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    messages = await crud_chat.get_messages(db, current_user_id, other_user_id)
    return messages

@router.put("/messages/read")
async def mark_messages_read(
    req: ChatMessageReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    await crud_chat.mark_messages_read(db, req.message_ids, current_user_id)
    return {"detail": "Messages marked as read"}

@router.delete("/messages")
async def delete_messages(
    req: ChatMessageDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    await crud_chat.delete_messages(db, req.message_ids, current_user_id, req.delete_type)
    return {"detail": "Messages deleted"}

@router.delete("/messages/all/{friend_id}")
async def delete_all_messages(
    friend_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    messages = await crud_chat.get_messages(db, current_user_id, friend_id)
    if messages:
        message_ids = [msg.id for msg in messages]
        await crud_chat.delete_messages(db, message_ids, current_user_id, 'me')
    return {"detail": "All messages deleted"}
