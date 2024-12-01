from aiogram.dispatcher.filters.state import State, StatesGroup


class PhoneNumberState(StatesGroup):
    phone_number = State()


class WikipediaState(StatesGroup):
    wiki = State()


class QrcodeState(StatesGroup):
    photo = State()


class TranslationState(StatesGroup):
    text = State()


class CalculatorState(StatesGroup):
    number = State()


# class DownloaderState(StatesGroup):
#     download = State()


class File(StatesGroup):
    out = State()


class Wiki(StatesGroup):
    loop = State()


class Download_yt(StatesGroup):
    loop = State()


class RBP(StatesGroup):
    loop = State()


class DownloadersState(StatesGroup):
    main = State()
    yt = State()
    insta = State()


class LevelState(StatesGroup):
    level = State()
    answer = State()
