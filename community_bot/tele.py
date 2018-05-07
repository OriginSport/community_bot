import logging
import telegram
import json

from django.http import HttpResponse
from django.conf import settings
from community_bot.reply.models import Reply


global bot
bot = telegram.Bot(token=settings.TELEGRAM_BOT_KEY)


def JSONResponse(data):
    return HttpResponse(data, content_type='application/json')

def verification(request):
    data = json.loads(request.body.decode('utf-8'))
    update = telegram.Update.de_json(data, bot)
    if update is None:
        return JSONResponse("Show me your TOKEN please!")
    # logging.info("Calling {}".format(update.message))
    handle_message(update.message)
    return JSONResponse("ok")

def get_content(text, lang):
    key = text.split('/')[-1]
    return Reply.get_content(key, lang)

def handle_message(msg):
    if not msg:
        return
    text = msg.text
    if not '/' in text and '@' in text:
        return
    if msg.chat.id == settings.TELEGRAM_CHINESE_CHANNEL:
        lang = 'zh_cn'
    else:
        lang = 'en_us'
    content = get_content(text, lang)
    if content:
        bot.sendMessage(chat_id=msg.chat.id, text=content)

