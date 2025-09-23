from telethon import TelegramClient, events
import config
import os

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

client = TelegramClient(config.session_name, config.api_id, config.api_hash)

async def main():
    # Авторизация пользователя
    await client.start()
    
    # Отображение списка чатов
    #async for dialog in client.iter_dialogs():
    #    print(dialog.name, 'has ID', dialog.id)
        
    # Отправка простого сообщения себе в ИЗБРАННОЕ
    #me = await client.get_me()
    #await client.send_message('me', 'Привет! Это сообщение отправлено моим первым клиентом.')

    last_id = read_last_id()
    messages = []
    async for message in client.iter_messages(config.source_chat_id, reverse=True):
        if last_id and message.id <= last_id:
            continue
        messages.append(message)
        if len(messages) >= config.limit:
            break

    for message in messages:
        print(f"{message.id}, {message.date}: {message.text} ")
        has_media = any([
            message.photo,
            message.video_note,
            message.voice,
            message.document,
            message.audio
        ])

        # Если только текст
        if message.text and not has_media:
            await client.send_message(config.target_chat_id, message.text)

        # Фото
        if message.photo:
            file = await message.download_media(progress_callback=progress_callback)
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        # Кружочки (video_note)
        if message.video_note:
            file = await message.download_media(progress_callback=progress_callback)
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        # Голосовые сообщения (voice)
        if message.voice:
            file = await message.download_media(progress_callback=progress_callback)
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        # Документы (document)
        if message.document:
            file = await message.download_media(progress_callback=progress_callback)
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        # Аудиофайлы (audio)
        if message.audio:
            file = await message.download_media(progress_callback=progress_callback)
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        write_last_id(message.id)

with client:
    client.loop.run_until_complete(main())