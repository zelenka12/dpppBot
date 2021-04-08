import logging
from config import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)  # add bot token
dp = Dispatcher(bot, storage=MemoryStorage())
connection = psycopg2.connect(database="de5kuesnfcrulq",
                              user="dlfclsnqthaqfw",
                              password="3fd5cb1203005f2937891cec7089c8801b9e6340609eb877adc5130f9eecf4da",
                              host="ec2-34-254-69-72.eu-west-1.compute.amazonaws.com",
                              port="5432")

cursor = connection.cursor()

class Register_state(StatesGroup):
    f_name = State()
    old = State()
    stanucya = State()
    poshta = State()


@dp.message_handler(commands=['start'])  # cmd_start
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Зареєструватися'))
    kb.add(types.KeyboardButton('Інформація'))
    kb.add(types.KeyboardButton('Видалити реєстрацію'))
    await message.answer('''СКОБ! Друже\Подруго!''', reply_markup=kb)

@dp.message_handler(lambda message: message.text == 'Видалити реєстрацію')
async def gel_reg(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT user_id FROM subs')
    data = cursor.fetchall()
    subs_ids = []
    for id in data:
        subs_ids.append(id[0])
    if user_id in subs_ids:
        cursor.execute(f"""DELETE FROM subs WHERE user_id='{user_id}'""")
        await message.answer('Видалено')
    else:
        await message.answer('Ти не зареєстрований!')
    connection.commit()

@dp.message_handler(lambda message: message.text == "Зареєструватися", state=None)
async def register(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT user_id FROM subs')
    data = cursor.fetchall()
    subs_ids = []
    for id in data:
        subs_ids.append(id[0])
    if user_id in subs_ids:
        await message.answer('Ви вже зареєстровані!')
    else:
        await message.answer("Напиши своє ім'я та прізвище")
        await Register_state.f_name.set()

@dp.message_handler(state=Register_state.f_name)
async def f_name(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(f_name=answer)
    await Register_state.next()
    await message.answer('Скільки тобі років?')

@dp.message_handler(state=Register_state.old)
async def old(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(old=answer)
    await Register_state.next()
    await message.answer('З якої Станиці?')

@dp.message_handler(state=Register_state.stanucya)
async def stanucya(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(stanucya=answer)
    await Register_state.next()
    await message.answer('Вкажи, будь ласка, найближче відділення Нової пошти')

@dp.message_handler(state=Register_state.poshta)
async def poshta(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(poshta=answer)
    username = message.from_user.username
    user_id = message.from_user.id
    user_data = await state.get_data()
    f_name = user_data.get('f_name')
    old = user_data.get('old')
    stanucya = user_data.get('stanucya')
    poshta = user_data.get('poshta')
    data = cursor.fetchall()
    subs_ids = []
    for id in data:
        subs_ids.append(id[0])
    if user_id not in subs_ids:
        cursor.execute(
            f"INSERT INTO subs (username,f_name,old,user_id,stanucya,poshta) "
            f"VALUES ('{username}', '{f_name}', '{old}', '{user_id}', '{stanucya}', '{poshta}')")
        connection.commit()
    else:
        cursor.execute(f"UPDATE subs SET username='{username}',f_name='{f_name}', "
                       f"old='{old}',user_id='{user_id}',stanucya='{stanucya}', poshta='{poshta}' "
                       f"WHERE user_id={user_id}")
        connection.commit()
    await message.answer('Реєстрація Успішна')
    await state.finish()

@dp.message_handler(lambda message: types.Message)
async def info(message: types.Message):
    await message.answer('''Я інтерактивний чат-бот, що стане твоїм єдиним інструктором у квесті до Дня першої пластової присяги. 
    Захід буде транслюватися онлайн 11 квітня. Початок квесту: 10:00. Усю потрібну інформацію відправлю тобі трохи пізніше - слідкуй за оновленнями.

Вразі виникнення проблем із ботом пропонуємо наступний алгоритм дій:
1. Перезапустити бота(введіть в чаті команду /start)
2. Не помогло? Тоді пишіть сюди: @zelenkkkaaaaa''')

if __name__ == "__main__":  # start polling
    executor.start_polling(dp, skip_updates=True)
