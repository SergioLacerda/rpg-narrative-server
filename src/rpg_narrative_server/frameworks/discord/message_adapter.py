async def send_message(message, content: str):
    await message.channel.send(content)
