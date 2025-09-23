from telethon import TelegramClient, events
import config
import os
from telethon.errors import PhotoInvalidDimensionsError

LAST_ID_FILE = 'last_message_id.txt'

def read_last_id():
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except Exception:
                return None
    return None

def write_last_id(msg_id):
    with open(LAST_ID_FILE, 'w') as f:
        f.write(str(msg_id))

def progress_callback(current, total):
    percent = int(current * 100 / total) if total else 0
    print(f"Скачано {current} из {total} байт ({percent}%)", end='\r')

def progress_up_callback(current, total):
    percent = int(current * 100 / total) if total else 0
    print(f"Отправлено {current} из {total} байт ({percent}%)", end='\r')

client = TelegramClient(config.session_name, config.api_id, config.api_hash)

async def main():
    # Авторизация пользователя
    await client.start()
    
    last_id = read_last_id()
    messages = []
    async for message in client.iter_messages(config.source_chat_id, reverse=True):
        if last_id and message.id <= last_id:
            continue
        messages.append(message)
        if len(messages) >= config.limit:
            break

    for message in messages:
        caption = message.text if message.text else None
        file = None
        media_type = None

        match True:
            case _ if message.photo:
                media_type = 'photo'
            case _ if message.video_note:
                media_type = 'video_note'
            case _ if message.voice:
                media_type = 'voice'
            case _ if message.audio:
                media_type = 'audio'
            case _ if getattr(message, 'video', None):
                media_type = 'video'
            case _ if message.document:
                media_type = 'document'
            case _:
                pass

        if message.text and not media_type:
            media_type = 'text'     

        print(f"{message.id} / {messages.__len__()+last_id}, {media_type}, {message.date}: {message.text} ")

        match True:
            case _ if message.photo:
                file = await message.download_media(progress_callback=progress_callback)
            case _ if message.video_note:
                file = await message.download_media(progress_callback=progress_callback)
            case _ if message.voice:
                file = await message.download_media(progress_callback=progress_callback)
            case _ if message.audio:
                file = await message.download_media(progress_callback=progress_callback)
            case _ if getattr(message, 'video', None):
                file = await message.download_media(progress_callback=progress_callback)
            case _ if message.document:
                file = await message.download_media(progress_callback=progress_callback)
            case _:
                pass

        if file:
            try:
                await client.send_file(config.target_chat_id, file, caption=f"{message.date}: {caption}", progress_callback=progress_up_callback)
            except PhotoInvalidDimensionsError:
            # если не проходит как фото — отправляем как документ
                print("PhotoInvalidDimensionsError: отправляем как документ")
                await client.send_file(config.target_chat_id, file, caption=f"{message.date}: {caption}", progress_callback=progress_up_callback, force_document=True)
            if file and os.path.exists(file):
                os.remove(file)
        elif message.text:
            await client.send_message(config.target_chat_id,  f"{message.date}: {message.text}")

        write_last_id(message.id)

with client:
    client.loop.run_until_complete(main())