import requests  
import time  
import PIL
from PIL import Image  
from io import BytesIO  
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton  
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TELEGRAM_BOT_TOKEN = '8398756165:AAFRdeGkft_JCvD4oQkRj6HNGh8cGZrDv-w'
LEONARDO_API_TOKEN = "4fd5808c-e080-4b1d-a42a-78ed2b3914bf"

def translate_to_english(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": "en",
        "dt": "t",
        "q": text  
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        translation = data[0][0][0]
        return translation  
    except requests.exceptions.RequestException as e:
        return f"Ошибка перевода: {e}"

def generate_image_leonardo(prompt):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "modelId": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",
        "seed": 1994276235,
        "sd_version": "KINO_2_1",
        "alchemy": False,
        "promptMagic": False,
        "highContrast": False,
        "transparency": "disabled",
        "ultra": False,
        "public": True,
        "styleUUID": "111dc692-d470-4eec-b791-3475abac4c46",
        "elements": [],
        "userElements": [],
        "controlnets": [],
        "contextImages": []
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer " + LEONARDO_API_TOKEN  
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        generation_id = response.json()["sdGenerationJob"]["generationId"]

        for _ in range(10):
            time.sleep(1.5)
            get_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()

            links = response.json()["generations_by_pk"]["generated_images"]
            if links:
                return links[0]["url"]

        return None    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при работе с Leonardo.Ai API: {e}")
        return None  
    except KeyError as e:
        print(f"Неожиданный формат ответа от Leonardo.Ai API: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Кошка"), KeyboardButton("Собака")],
        [KeyboardButton("Чистая генерация")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Привет 👋! Я бот, который может создавать изображения. Выбери один из вариантов:',
        reply_markup=reply_markup  
    )

async def dog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Собака на луне готовится. ЖДИ")
    
    translated_text = translate_to_english('собака на луне')
    await update.message.reply_text("Готовлю изображение, так что погоди.")
    
    image_link = generate_image_leonardo(translated_text)

    if image_link:
        try:
            image_response = requests.get(image_link)
            image_response.raise_for_status()
            img_data = image_response.content  
            image = Image.open(BytesIO(img_data))

            with BytesIO() as output:
                image.save(output, format="PNG")
                output.seek(0)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output, caption="Вот твоя собака на луне!")
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"Произошла ошибка при скачивании изображения: {e}")
        except Exception as e:
            await update.message.reply_text("Подожди, дай подумать.")
    else:
        await update.message.reply_text("Не удалось сгенерировать изображение. Попробуйте еще раз или измените запрос.")

async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Кошка за столом готовится. ЖДИ")
    
    translated_text = translate_to_english('Кошка за столом')
    await update.message.reply_text("Готовлю изображение, так что погоди.")
    
    image_link = generate_image_leonardo(translated_text)

    if image_link:
        try:
            image_response = requests.get(image_link)
            image_response.raise_for_status()
            img_data = image_response.content  
            image = Image.open(BytesIO(img_data))

            with BytesIO() as output:
                image.save(output, format="PNG")
                output.seek(0)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output, caption="Вот твоя кошка за столом!")
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"Произошла ошибка при скачивании изображения: {e}")
        except Exception as e:
            await update.message.reply_text("Подожди, дай подумать.")
    else:
        await update.message.reply_text("Не удалось сгенерировать изображение. Попробуйте еще раз или измените запрос.")

async def per_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  
    if not args:
        await update.message.reply_text("НАПИШИ В ЧАТ ЧТО ХОЧЕШЬ СГЕНЕРИРОВАТЬ Например: </per собака на луне>")
        return

    input_text = " ".join(args)
    translated_text = translate_to_english(input_text)
    await update.message.reply_text("Готовлю изображение, так что погоди.")
    
    image_link = generate_image_leonardo(translated_text)

    if image_link:
        try:
            image_response = requests.get(image_link)
            image_response.raise_for_status()
            img_data = image_response.content  
            image = Image.open(BytesIO(img_data))

            with BytesIO() as output:
                image.save(output, format="PNG")
                output.seek(0)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output, caption="Вот твоя картинка!")
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"Произошла ошибка при скачивании изображения: {e}")
        except Exception as e:
            await update.message.reply_text("Подожди, дай подумать.")
    else:
        await update.message.reply_text("Не удалось сгенерировать изображение. Попробуйте еще раз или измените запрос.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_text = update.message.text  
    if button_text == "Кошка":
        await cat(update, context)
    elif button_text == "Собака":
        await dog_command(update, context)
    elif button_text == "Чистая генерация":
        await per_command(update, context)

def main():
    print("Бот запускается...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("per", per_command))
    application.add_handler(CommandHandler("dog", dog_command))
    application.add_handler(CommandHandler("cat", cat))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

    application.run_polling()
    print("Бот остановлен.")

if __name__ == '__main__':
    main()
