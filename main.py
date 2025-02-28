import asyncio
import os
import logging
import random
from io import BytesIO
import tempfile
import requests
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from fpdf import FPDF
from PIL import Image
from rembg import remove
from googletrans import Translator
import wikipedia
import qrcode

from kurs_view import url
from state import PhoneNumberState, WikipediaState, QrcodeState, LevelState, TranslationState, RBP, File, \
    DownloadersState
from keyboard import main_menu, back_button, pdf_creation_keyboard, main_downloader, level_button, stop_button, stop_button2

BOT_TOKEN = ''
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# API_KEY = ""
# url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/USD/UZS"

wikipedia.set_lang("uz")
translator = Translator()

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start', 'help'], state="*")
async def send_message(message: types.Message, state: FSMContext):
    await message.answer("""Salom bu mening universal telegram botim,
bu botda dollar kursi, tarjimon, youtube, instagram video 
yuklab olish imkonyatlari bor""", reply_markup=main_menu())
    await state.finish()


@dp.message_handler(Text("Back🔙"), state="*")
async def stop_handler(msg: types.Message, state: FSMContext):
    await msg.answer('Back🔙', reply_markup=main_menu())
    await state.finish()


@dp.message_handler(Text(equals='Downloaders'))
async def send_welcome(message: types.Message):
    await message.reply("Toifani tanlang!", reply_markup=main_downloader())
    await DownloadersState.main.set()


@dp.message_handler(Text(equals='Instagram'), state=DownloadersState.main)
async def send_welcome(message: types.Message):
    await message.reply("Salom! Instagram media yuklovchi botga xush kelibsiz!\n"
                        "Iltimos, Instagram video yoki rasm URL manzilini yuboring.", reply_markup=back_button())
    await DownloadersState.insta.set()


@dp.message_handler(Text(equals='YouTube'), state=DownloadersState.main)
async def send_welcome(message: types.Message):
    await message.reply("Salom! Men YouTube videolarini yuklab olish uchun botman. \n"
                        "Video yuklab olish uchun menga YouTube URL manzilini yuboring.", reply_markup=back_button())
    await DownloadersState.yt.set()


@dp.message_handler(Text(startswith='https://www.youtube.com'), state=DownloadersState.yt)
async def download_video(message: types.Message):
    video_url = message.text.strip()

    ydl_opts = {
        'outtmpl': './%(title)s.%(ext)s',
        'format': 'best',
    }

    try:
        await message.reply("Video yuklab olinmoqda, biroz kuting...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info_dict)

        with open(file_name, 'rb') as video:
            await message.reply_video(video)
            os.remove(file_name)

    except Exception as e:
        await message.reply(f"Video yuklab olishda xato: {e}")


def download_instagram_media(url):
    ydl_opts = {
        'outtmpl': './%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(result)
            return file_path, None
    except Exception as e:
        return None, str(e)


@dp.message_handler(content_types=types.ContentType.TEXT, state=DownloadersState.insta)
async def handle_instagram_url(message: types.Message):
    url = message.text.strip()

    if not url.startswith("http"):
        await message.reply("Iltimos, to‘g‘ri URL manzilini yuboring.")
        return

    await message.reply("Media yuklanmoqda, biroz kuting...")

    file_path, error = await asyncio.to_thread(download_instagram_media, url)

    if file_path:

        with open(file_path, 'rb') as file:
            await message.reply_document(file)

        os.remove(file_path)
    else:
        await message.reply(f"Media yuklab olishda xato yuz berdi: {error}")


@dp.message_handler(Text(equals='Photo to pdf'), state=None)
async def start_photo_to_pdf(message: types.Message):
    await message.answer("Rasm tashlang (Bitta yoki bir nechta rasm yuboring)", reply_markup=back_button())
    await File.out.set()


@dp.message_handler(state=File.out, content_types=['photo'])
async def handle_docs_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'photos' not in data:
            data['photos'] = []

        photo = message.photo[-1]
        photo_file = await photo.download(destination=BytesIO())
        photo_file.seek(0)

        data['photos'].append(photo_file)

        await message.answer("Yana rasm yuboring yoki PDF yaratish uchun quyidagi tugmani bosing:",
                             reply_markup=pdf_creation_keyboard())


@dp.callback_query_handler(state=File.out)
async def create_pdf(callback_query: types.CallbackQuery, state: FSMContext):
    requests = callback_query.data
    if requests == 'create_pdf':
        async with state.proxy() as data:
            if 'photos' not in data or not data['photos']:
                await callback_query.message.answer("Hech qanday rasm yuborilmadi!")
                return

            pdf_path = f"pdfs/{callback_query.from_user.id}_{random.randint(1000, 9999)}.pdf"
            os.makedirs('pdfs', exist_ok=True)

            pdf = FPDF()
            for photo_file in data['photos']:
                photo_file.seek(0)
                image = Image.open(photo_file)

                image_format = image.format.lower()
                if image_format not in ['jpeg', 'png']:
                    image_format = 'png'

                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{image_format}') as temp_file:
                    temp_file_path = temp_file.name
                    image.save(temp_file_path, format=image_format)

                    pdf.add_page()

                    max_width, max_height = 190, 270
                    image.thumbnail((max_width, max_height))
                    pdf.image(temp_file_path, x=10, y=10, w=image.width, h=image.height)

            pdf.output(pdf_path, "F")

            await bot.send_document(callback_query.from_user.id, InputFile(pdf_path))

            os.remove(pdf_path)
            data['photos'] = []

        await callback_query.message.answer("PDF yaratildi! Yana bir narsa qilishni xohlaysizmi?",
                                            reply_markup=main_menu())

        await state.finish()


@dp.message_handler(Text(equals="Remove Background"))
async def start_remove_background(message: types.Message):
    await message.reply("Salom! 😊 Men rasmning orqa fonini olib tashlayman. Menga rasm yuboring!",
                        reply_markup=back_button())
    await RBP.loop.set()


@dp.message_handler(state=RBP.loop, content_types=[ContentType.PHOTO])
async def handle_remove_bg_photo(message: types.Message):
    photo = message.photo[-1]
    photo_file = await photo.download(destination=BytesIO())
    photo_file.seek(0)

    output_image = remove(photo_file.read())

    output_io = BytesIO(output_image)
    output_io.seek(0)

    await bot.send_document(chat_id=message.chat.id, document=types.InputFile(output_io, filename="removed_bg.png"),
                            caption="Orqa fon olib tashlandi! 🏞️")
    await RBP.loop.set()


@dp.message_handler(Text(equals="dollar"))
async def start_remove_background(message: types.Message):
    response = requests.get(url)
    json_data = response.json()
    kurs = json_data['conversion_rate']
    await message.reply(f"Bugungi 1$ narxi {kurs} So'm",
                        reply_markup=main_menu())


@dp.message_handler(Text(equals="Tarjimon"))
async def send_message(message: types.Message):
    await message.answer(text="""Tarjimon botimizga xush kelibsiz!
    Uzbek 🔁 English""", reply_markup=back_button())
    await TranslationState.text.set()


@dp.message_handler(state=TranslationState.text)
async def send_translate(message: types.Message, state: FSMContext):
    tarjimon = translator.translate(text=message.text, src="uz", dest="en")
    await message.answer(text=tarjimon.text)
    await TranslationState.text.set()


@dp.message_handler(Text(equals="savol javob"))
async def bot_start(message: types.Message):
    await message.answer(f"Salom, {message.from_user.full_name}!",
                         reply_markup=level_button())
    await message.answer_photo("https://telegra.ph/file/8b13919c076e881fde66b.png",
                               caption=f"Hush kelibsiz {message.from_user.first_name}"
                                       f" bilag'on \nsizga bir nechta savolar berib "
                                       f"bilimingizni tekshirib beramiz !")
    await LevelState.level.set()


@dp.message_handler(Text(equals="wikipedia"))
async def send_message(message: types.Message):
    await message.answer(text="Wikipedia qismiga xush kelibmiz", reply_markup=back_button())
    await WikipediaState.wiki.set()


@dp.message_handler(state=WikipediaState.wiki)
async def send_message(message: types.Message, state: FSMContext):
    try:

        text = wikipedia.summary(message.text, sentences=3)
        await message.answer(text=text)
        await WikipediaState.wiki.set()
    except wikipedia.exceptions.DisambiguationError as e:

        await message.answer("Sizning so'rovingiz juda noaniq. Iltimos, batafsilroq belgilang.\n"
                             f"Takliflar: {', '.join(e.options[:5])}")
        await WikipediaState.wiki.set()

    except wikipedia.exceptions.PageError:

        await message.answer("Ma'lumot topilmadi!")
        await WikipediaState.wiki.set()


@dp.message_handler(Text(equals="qrcode"))
async def send_message(message: types.Message):
    await message.answer(text="Link kiriting", reply_markup=back_button())
    await QrcodeState.photo.set()


@dp.message_handler(Text(startswith="https://"), state=QrcodeState.photo)
async def send_message(message: types.Message, state: FSMContext):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=1,
    )
    qr.add_data(message.text)
    qr.make(fit=True)

    image = qr.make_image(fill_color="green", back_color="white")
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    await message.answer_photo(photo=buffer, reply_markup=main_menu())
    await state.finish()


@dp.message_handler(state=QrcodeState.photo)
async def send_message(message: types.Message, state: FSMContext):
    await message.answer("Warning! Link begin https://")


@dp.message_handler(state=LevelState.level)
async def lvl_handler(msg: types.Message, state: FSMContext):
    if msg.text == "LEVEL 1️⃣":
        question = f"{random.randrange(1, 11)} {random.choice(['+', '-', '*'])} {random.randrange(1, 11)}"
        answer = eval(question)
    elif msg.text == "LEVEL 2️⃣":
        question = f"{random.randrange(1, 51)} {random.choice(['+', '-', '*'])} {random.randrange(1, 51)}"
        answer = eval(question)
    elif msg.text == "LEVEL 3️⃣":
        question = f"{random.randrange(1, 101)} {random.choice(['+', '-', '*'])} {random.randrange(1, 101)}"
        answer = eval(question)
    elif msg.text == "LEVEL 4️⃣":
        question = f"{random.randrange(1, 101)} {random.choice(['+', '-', '*', '/'])} {random.randrange(1, 101)}"
        answer = eval(question)

    async with state.proxy() as data:
        data["answer"] = answer
        data['level'] = msg.text
        data['true'] = 0
        data['false'] = 0
    await LevelState.next()
    await msg.answer(f"SAVOL : {question}  = ?", reply_markup=stop_button())


@dp.message_handler(Text("🛑 Stop"), state=LevelState.answer)
async def stop_handler(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        true_answer = data["true"]
        false_answer = data["false"]

        text = f"""{data["level"]}
Savolarning soni : {int(true_answer) + int(false_answer)}:
✅ : {true_answer}
❌ : {false_answer}"""
    await msg.answer(text,
                     reply_markup=level_button())
    await LevelState.level.set()


@dp.message_handler(state=LevelState.answer)
async def start_test(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data.get("answer") == int(msg.text):
            data["true"] += 1
            await msg.answer("✅")
        else:
            data["false"] += 1
            await msg.answer("❌")

        if data.get('level') == "LEVEL 1️⃣":
            question = f"{random.randrange(1, 11)} {random.choice(['+', '-', '*'])} {random.randrange(1, 11)}"
            answer = eval(question)
        elif data.get('level') == "LEVEL 2️⃣":
            question = f"{random.randrange(1, 51)} {random.choice(['+', '-', '*'])} {random.randrange(1, 51)}"
            answer = eval(question)
        elif data.get('level') == "LEVEL 3️⃣":
            question = f"{random.randrange(1, 101)} {random.choice(['+', '-', '*'])} {random.randrange(1, 101)}"
            answer = eval(question)
        elif data.get('level') == "LEVEL 4️⃣":
            question = f"{random.randrange(1, 101)} {random.choice(['+', '-', '*', '/'])} {random.randrange(1, 101)}"
            answer = eval(question)

        data["answer"] = answer

    await LevelState.answer.set()
    await msg.answer(f"SAVOL : {question}  = ?", reply_markup=stop_button())


@dp.message_handler(Text(equals="Phone number"))
async def send_message(message: types.Message):
    await message.answer(text="Telefon raqamni kiriting",
                         reply_markup=stop_button2())
    await PhoneNumberState.phone_number.set()


@dp.message_handler(Text(equals="⛔️ Stop"), state=PhoneNumberState.phone_number)
async def send_message(message: types.Message, state: FSMContext):
    await message.answer(text="Ortga", reply_markup=main_menu())
    await state.finish()


@dp.message_handler(state=PhoneNumberState.phone_number)
async def send_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await message.answer(text=f"https://t.me/{data['phone_number']}")
    await PhoneNumberState.phone_number.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

'''BOT TOKEN
 ### 
    6600411974:AAFAi9oXPnoTdDXszehmP54Tca2a3iiTy3Y 
 ###'''
