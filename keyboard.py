from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def pdf_creation_keyboard():
    """Generate an inline keyboard with a 'PDF yaratish' button."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📄 PDF yaratish", callback_data="create_pdf"))
    return keyboard


def main_menu():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(text="dollar")
    button2 = KeyboardButton(text="Photo to pdf")
    # button2 = KeyboardButton(text="username")
    button3 = KeyboardButton(text="wikipedia")
    button4 = KeyboardButton(text="qrcode")
    button5 = KeyboardButton(text="Tarjimon")
    button6 = KeyboardButton(text="savol javob")
    button7 = KeyboardButton(text="Downloaders")
    button8 = KeyboardButton(text="Remove Background")
    button9 = KeyboardButton(text="Phone number")
    rkm.row(button, button2, button3)
    rkm.row(button4, button5, button6)
    rkm.row(button7, button8, button9)
    return rkm


def main_downloader():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(text="Instagram")
    button2 = KeyboardButton(text="YouTube")
    button7 = KeyboardButton(text="Back🔙")
    rkm.row(button, button2)
    rkm.row(button7)
    return rkm


def level_button():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add("LEVEL 1️⃣", "LEVEL 2️⃣")
    rkm.add("LEVEL 3️⃣", "LEVEL 4️⃣")
    rkm.add("Back🔙")
    return rkm


def stop_button():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add("🛑 Stop")
    return rkm


def stop_button2():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add("⛔️ Stop")
    return rkm


def back_button():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm.add("Back🔙")
    return rkm
