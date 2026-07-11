import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.models.chat import Friendship, FriendshipStatus, ChatMessage
from app.models.user import User

async def search_users(db: AsyncSession, query: str):
    stmt = select(User).where(
        or_(
            User.email.ilike(f"%{query}%"),
            User.full_name.ilike(f"%{query}%")
        )
    ).limit(10)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_friendship_request(db: AsyncSession, requester_id: uuid.UUID, addressee_id: uuid.UUID) -> Friendship:
    stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(
        or_(
            and_(Friendship.requester_id == requester_id, Friendship.addressee_id == addressee_id),
            and_(Friendship.requester_id == addressee_id, Friendship.addressee_id == requester_id)
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    new_friendship = Friendship(requester_id=requester_id, addressee_id=addressee_id)
    db.add(new_friendship)
    await db.commit()
    
    # Reload with relationships
    stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(Friendship.id == new_friendship.id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_friend_requests(db: AsyncSession, user_id: uuid.UUID):
    stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_friends_list(db: AsyncSession, user_id: uuid.UUID):
    stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(
        or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_friendship_status(db: AsyncSession, friendship_id: uuid.UUID, status: FriendshipStatus):
    stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(Friendship.id == friendship_id)
    result = await db.execute(stmt)
    friendship = result.scalar_one_or_none()
    if friendship:
        friendship.status = status
        await db.commit()
        # Reload with relationships after commit to avoid lazy load issues
        stmt = select(Friendship).options(selectinload(Friendship.requester), selectinload(Friendship.addressee)).where(Friendship.id == friendship_id)
        result = await db.execute(stmt)
        return result.scalar_one()
    return friendship

async def remove_friendship(db: AsyncSession, friendship_id: uuid.UUID):
    stmt = select(Friendship).where(Friendship.id == friendship_id)
    result = await db.execute(stmt)
    friendship = result.scalar_one_or_none()
    if friendship:
        await db.delete(friendship)
        await db.commit()
    return friendship

async def send_message(db: AsyncSession, sender_id: uuid.UUID, receiver_id: uuid.UUID, content: str):
    msg = ChatMessage(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, user1_id: uuid.UUID, user2_id: uuid.UUID):
    # filter out messages that are deleted for 'me'
    stmt = select(ChatMessage).where(
        or_(
            and_(
                ChatMessage.sender_id == user1_id, 
                ChatMessage.receiver_id == user2_id,
                ChatMessage.deleted_by_sender == False
            ),
            and_(
                ChatMessage.sender_id == user2_id, 
                ChatMessage.receiver_id == user1_id,
                ChatMessage.deleted_by_receiver == False
            )
        )
    ).order_by(ChatMessage.created_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def mark_messages_read(db: AsyncSession, message_ids: list[uuid.UUID], user_id: uuid.UUID):
    stmt = select(ChatMessage).where(
        ChatMessage.id.in_(message_ids),
        ChatMessage.receiver_id == user_id
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    for msg in messages:
        msg.is_read = True
    await db.commit()
    return messages

async def delete_messages(db: AsyncSession, message_ids: list[uuid.UUID], user_id: uuid.UUID, delete_type: str):
    stmt = select(ChatMessage).where(ChatMessage.id.in_(message_ids))
    result = await db.execute(stmt)
    messages = result.scalars().all()
    for msg in messages:
        if delete_type == 'everyone':
            if msg.sender_id == user_id:
                msg.deleted_for_everyone = True
        elif delete_type == 'me':
            if msg.sender_id == user_id:
                msg.deleted_by_sender = True
            elif msg.receiver_id == user_id:
                msg.deleted_by_receiver = True
    await db.commit()
