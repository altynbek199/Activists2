import socketio
from db.models.models_mongodb import Message

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")


@sio.event
async def connect(sid, environ):
    print(f'Client {sid} connected to common room')

    await sio.enter_room(sid, "common_room")

@sio.event
async def disconnect(sid):
    print(f'Client {sid} disconnected from common room')

    await sio.leave_room(sid, 'common_room')

@sio.event
async def message(sid, data: dict):
    print(f'Message was recieved from {sid}: {data}')
    text = data.get("text", "").strip()
    sender_id = data.get("sender_id")
    sender_name = data.get("sender_name", "Anonist") 

    if not text or not sender_id:
        return

    msg = await Message(
        sender_id=sender_id,
        sender_name=sender_name,
        text=text
    ).insert()

    await sio.emit(
        "new_message", {
         "id": str(msg.id),
         "sender_id": sender_id,
         "sender_name": sender_name,
         "text": text,
         "created_at": msg.created_at.isoformat()  
         },
         room="common_room",
         skip_sid=sid 
    )



