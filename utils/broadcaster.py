from aiogram.types import Message


async def send_copy(message: Message, chat_id: int):
    try:
        await message.send_copy(chat_id=chat_id)
        return True
    except:
        kwargs = {
            "chat_id": chat_id,
            "reply_markup": message.reply_markup,
        }
        text = message.text or message.caption
        entities = message.entities or message.caption_entities
        from core.misc import bot2
        try:
            if message.text:
                await bot2.send_message(text=message.text, **kwargs)
            if message.audio:
                await bot2.send_audio(
                    audio=message.audio.file_id,
                    caption=text,
                    title=message.audio.title,
                    performer=message.audio.performer,
                    duration=message.audio.duration,
                    caption_entities=entities,
                    **kwargs,
            )
            if message.document:
                await bot2.send_document(
                    document=message.document.file_id, caption=text, caption_entities=entities, **kwargs
                )
            if message.photo:
                await bot2.send_photo(
                    photo=message.photo[-1].file_id, caption=text, caption_entities=entities, **kwargs
                )
            if message.video:
                await bot2.send_video(
                    video=message.video.file_id, caption=text, caption_entities=entities, **kwargs
                )
            return True
        except:
            return False