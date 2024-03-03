from types import SimpleNamespace

import requests
import json
import os

from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

url = "https://stablediffusionapi.com/api/v3/text2img"
bot_key = os.getenv("BOT_API_KEY")
sd_key = os.getenv("STABLE_DIFFUSION_AI_KEY")
gpt_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=gpt_key,
)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет {update.effective_user.first_name}. Рад тебя увидит')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'/start - Команда для запуска бота\n'
                                    f'/help - Команда для получения помощи\n'
                                    f'/imagine (запрос) - Команда для генерации картинок\n'
                                    f'/ask (запрос) - Команда для получения ответа (GPT)')


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Запрос принять на обработку...')
    imageRequest = update.message.text.replace("/imagine", "")
    payload = json.dumps({
        "key": sd_key,
        "prompt": imageRequest,
        "negative_prompt": None,
        "width": "512",
        "height": "512",
        "samples": "1",
        "num_inference_steps": "20",
        "seed": None,
        "guidance_scale": 7.5,
        "safety_checker": "yes",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "no",
        "upscale": "no",
        "embeddings_model": None,
        "webhook": None,
        "track_id": None
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))
    await update.message.reply_text(f'Отправляю фото')
    print(data)
    await update.message.reply_photo(data.output[0])


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Запрос принять на обработку...')
    textRequest = update.message.text.replace("/ask", "")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": textRequest,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion)
    await update.message.reply_text(chat_completion.choices[0].message.content)


app = ApplicationBuilder().token(bot_key).build()

app.add_handler(CommandHandler("start", hello))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("imagine", imagine))
app.add_handler(CommandHandler("ask", ask))

app.run_polling()
