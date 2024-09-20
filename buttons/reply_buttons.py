from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Nomer Jonatish📞", request_contact=True)]
], resize_keyboard=True)

main_button_barber = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Yangi slot ochish➕")]
], resize_keyboard=True)

main_button_client = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Joyni band qilish🔒"), KeyboardButton(text="Lokatsiya olish📍")]
], resize_keyboard=True)


