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
        if len(messages) >= 10:
            break

    for message in messages:
        print(f"{message.id}, {message.date}: {message.text} ")
        # Копируем текст
        if message.text:
            await client.send_message(config.target_chat_id, message.text)
        # Копируем фото
        if message.photo:
            file = await message.download_media()
            await client.send_file(config.target_chat_id, file, caption=message.text if message.text else None)
            if file and os.path.exists(file):
                os.remove(file)
        write_last_id(message.id)

with client:
    client.loop.run_until_complete(main())