import io
import asyncio
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from services.celery_app import celery
from services.s3_service import s3_client 
from db.database import async_session_factory 
from db.dals import EventsDAL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from settings import settings
import uuid
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

register_heif_opener()
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

async def optimize_image_logic(event_id: uuid.UUID, s3_key: str) -> Optional[UUID]:    
    # Now we log details for debugging
    logger.info(f'EVENT_ID: {event_id} | S3_KEY: {s3_key}')
    
    filename_old = s3_key.split("/")[-1]
    logger.info(f'EXTRACTED FILENAME: {filename_old}')
    
    file_bytes = await s3_client.get_file(filename_old)
    
    # 2. Обработка Pillow (оставляем твою отличную логику)
    img = Image.open(io.BytesIO(file_bytes))
    img = ImageOps.exif_transpose(img)
    
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="WEBP", quality=80, method=6)
    output.seek(0)

    # 3. Генерируем новый путь для оптимизированного файла
    optimized_key = s3_key.replace(filename_old, f"optimized_{filename_old.split('.')[0]}.webp")
    filename_new = optimized_key.split("/")[-1]

    # 4. Загружаем обработанный файл обратно в S3 (ensure bytes are passed)
    url = await s3_client.upload_file(
        filename=filename_new,
        file=output.getvalue(),
    ) 

    await s3_client.delete_file(s3_key=filename_old)  # delete old version of image 
    
    # Create a new async engine/sessionmaker inside the worker process to
    # ensure connections are bound to the current event loop and avoid
    # 'Future attached to a different loop' issues.
    engine = create_async_engine(settings.DATABASE_ASYNC_URL)
    LocalSession = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with LocalSession() as session:
            async with session.begin():
                event_dal = EventsDAL(session)
                updated_event_id = await event_dal.update_photo(event_id=event_id, photo=url)
    finally:
        # Dispose the engine to close pool connections bound to this loop
        await engine.dispose()

    return updated_event_id    
            


    

@celery.task(name="optimize_image_task")
def optimize_image_task(event_id: uuid.UUID, s3_key: str) -> Optional[UUID]:
    # 'https://{self.static_domain}/{unique_filename}'
    return asyncio.run(optimize_image_logic(event_id, s3_key))