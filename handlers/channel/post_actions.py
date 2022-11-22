from aiogram import Router
from aiogram.types import CallbackQuery

from core.sessions import blocked_users_cache, like_action_counter
from db.crud import update_likes
from db.models import User, Post, PostLikes
from core.config import settings
from filters.callback_data import PostAction, LikeButton
from filters.common import IsAdmin, ChannelFilter
from localization.strings import _

router = Router()


@router.callback_query(IsAdmin(), PostAction.filter(), ChannelFilter(channel=settings.CONSIDERATION_CHANNEL_ID))
async def commit_action(call: CallbackQuery, user: User, callback_data: PostAction):
    from core.misc import bot
    post: Post = await Post.get(id=callback_data.post_id).prefetch_related('author', 'district', 'school')
    author: User = post.author
    if callback_data.action == 'reject':
        await bot.send_message(chat_id=author.tg_id, text=_('post_rejected', author.lang_code))
        await post.delete()
        text = call.message.caption + f"\n————————————————\n<b>🚫 Rejected by :</b>  {user.mention}"
        await call.message.edit_caption(caption=text, reply_markup=None)
    else:
        post.status = 'approved'
        await post.save()
        text = call.message.caption + f"\n\n<b>✅ Approved by:</b>  {user.mention}"
        await call.message.edit_caption(caption=text, reply_markup=None)


@router.callback_query(LikeButton.filter(), ChannelFilter(channel=settings.MAIN_CHANNEL_ID))
async def perform_like(call: CallbackQuery, user: User, callback_data: LikeButton):
    if not user.like_allowed:
        await call.answer(text=_('join_alert', user.lang_code), show_alert=True)
        return
    block_list_key = f'like_blocked:{user.tg_id}:{callback_data.counter_id}'

    if block_list_key in blocked_users_cache:
        await call.answer(text=_('too_many_requests', user.lang_code), show_alert=True)
        blocked_users_cache[block_list_key] = True
        return

    like_pressed_key = f'liked:{user.tg_id}:{callback_data.counter_id}'
    if like_pressed_key in like_action_counter:
        blocked_users_cache[block_list_key] = True
        await call.answer(text=_('too_many_requests', user.lang_code), show_alert=True)
        return
    like_action_counter[like_pressed_key] = True

    counter = await PostLikes.get(id=callback_data.counter_id).prefetch_related('post')
    existence = bool(await counter.liked_users.filter(id=user.pk))

    like_count = int(call.message.reply_markup.inline_keyboard[0][0].text.split()[1])
    previous = like_count
    if existence:
        if like_count > 0:
            like_count -= 1
        text = _('like_taken', user.lang_code)
    else:
        like_count += 1
        text = _('liked', user.lang_code)

    await call.answer(text=text, show_alert=True)
    if previous != like_count:
        call.message.reply_markup.inline_keyboard[0][0].text = f'👍 {like_count}'
        try:
            await call.message.edit_reply_markup(reply_markup=call.message.reply_markup)
        except:
            pass

    await update_likes(existence=existence, counter=counter, user=user)
