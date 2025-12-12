from api.actions.chat import sio, Message
from fastapi import APIRouter




chat_router = APIRouter()


@chat_router.get("/history")
async def get_history(limit: int = 50):
    messages = await Message.find_all().sort(-Message.created_at).limit(limit).to_list()
    messages.reverse()
    
    return [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "sender_name": m.sender_name,
            "text": m.text,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]




























