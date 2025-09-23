from telethon import TelegramClient, events
import config


client = TelegramClient(config.session_name, config.api_id, config.api_hash)

async def main():
    # Авторизация пользователя
    await client.start()
    
    # Отображение списка чатов
    #async for dialog in client.iter_dialogs():
    #    print(dialog.name, 'has ID', dialog.id)
        
    # Отправка простого сообщения себе
    #me = await client.get_me()
    await client.send_message('me', 'Привет! Это сообщение отправлено моим первым клиентом.')

with client:
    client.loop.run_until_complete(main())