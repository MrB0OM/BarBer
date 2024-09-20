import datetime
from aiogram import Bot, Dispatcher
import asyncio
from config import TOKEN, ADMIN, CHANNEL_ID
from database import Database
from aiogram import filters, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from buttons.reply_buttons import (contact_button, main_button_barber, main_button_client)
from aiogram.types import (ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton)


bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
db = Database()



class Registration(StatesGroup):
    full_name = State()
    phone_number = State()


class Time(StatesGroup):
    start_time = State()
    end_time = State()


async def is_user_subscribed(user_id: int):
    chat_number = await bot.get_chat_member(CHANNEL_ID, user_id)
    return chat_number.status

async def reminder_function():
    while True:
        current_time = datetime.datetime.now()
        slots = db.get_all_available_time()
        for slot in slots:
            start_time_str = slot[0]
            start_time = datetime.datetime.strptime(start_time_str, '%H:%M')
            if start_time - current_time <= datetime.timedelta(minutes=10):
                await bot.send_message(ADMIN, f"Напоминание: у вас забронировано время на {start_time_str}")
        await asyncio.sleep(60)




@dp.message(filters.Command("start"))
async def start_function(message: types.Message, state: FSMContext):
    is_subscribed = await is_user_subscribed(user_id=message.from_user.id)
    if is_subscribed == 'left':
        await message.answer("Salom user👋 agar kanalimizga obuna bolmasangiz men ishlamayman❌!")
        await message.answer("t.me/testnumber2forpython")
        return

    user_check = db.check_user(message.from_user.id)
    if user_check is None:
        await state.set_state(Registration.full_name)
        await message.answer("Salom user👋 iltimos menga ismingiz va familiyangizni jonating📬!")
    else:
        if message.from_user.id == ADMIN:
            await message.answer("Qaytishingiz bilan😊!", reply_markup=main_button_barber)
        else:
            await message.answer('Qaytishingiz bilan😊!', reply_markup=main_button_client)


@dp.message(Registration.full_name)
async def full_name_function(message: types.Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await state.set_state(Registration.phone_number)
    await message.answer("Zo'r endi esa menga nomeringizni jonating📬 jonatish uchun tugmani bosing👇 ", reply_markup=contact_button)


@dp.message(Registration.phone_number)
async def phone_number_function(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    data = await state.get_data()
    db.add_user(id=message.from_user.id, full_name=data['full_name'], phone_number=phone_number)

    await state.update_data(phone_number=phone_number)
    await state.clear()

    if message.from_user.id == ADMIN:
        await message.answer("Yaxshi biz informatsiyani saqlab oldik🔐", reply_markup=main_button_barber)
    else:
        await message.answer("Yaxshi biz informatsiyani saqlab oldik🔐", reply_markup=ReplyKeyboardRemove())


@dp.message(F.text == "Yangi slot ochish➕")
async def slot_function(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer("Qachon vaqtingiz bolishini jonating🕐")
        await state.set_state(Time.start_time)
    else:
        await message.answer("Siz kimsiz biz sizni chaqirmagandik😡")


@dp.message(Time.start_time)
async def start_time_function(message: types.Message, state: FSMContext):
    start_time = message.text
    await state.update_data(start_time=start_time)
    await state.set_state(Time.end_time)
    await message.answer("Qancha voqtiga bosh bolasiz 1 dona clinet uchun🧔")


@dp.message(Time.end_time)
async def end_time_function(message: types.Message, state: FSMContext):
    end_time = message.text
    await state.update_data(end_time=end_time)
    await message.answer("Yaxshi biz yangi slot ochdik✅!")
    data = await state.get_data()
    db.add_time(start_time=data["start_time"], end_time=data["end_time"])
    await state.clear()


@dp.message(F.text == "Joyni band qilish🔒")
async def book_slot_function(message: types.Message):
    all_slots = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    slots = db.get_all_available_time()
    for slot in slots:
        data = [KeyboardButton(text=f"{slot[0]} - {slot[1]}")]
        all_slots.keyboard.append(data)
    all_slots.keyboard.append([KeyboardButton(text="Назад")])
    await message.answer("Sizga mos bolgan voqtni tallang🕔", reply_markup=all_slots)


@dp.message(F.text == "Назад")
async def back_function(message: types.Message):
    await message.answer("Siz ortga qayttingiz⬅️", reply_markup=main_button_client)


@dp.message(F.text == "Lokatsiya olish📍")
async def location_function(message: types.Message):
    await message.answer_location(41.2722, 69.2049)


@dp.message(F.text)
async def button_function(message: types.Message):
    data = message.text.split()
    if data:
        start_time = data[0]
        end_time = data[2]
        db.book_slot(start_time, end_time)
        await message.answer(f"Вы забронировали это время: {start_time} - {end_time}", reply_markup=main_button_client)
    else:
        await message.answer("Нет мест")





async def main():
    # Create a task for the reminder function
    asyncio.create_task(reminder_function())
    # Start polling with the dispatcher
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
