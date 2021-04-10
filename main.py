import logging
from config import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from kvest import kvest

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)  # add bot token
dp = Dispatcher(bot, storage=MemoryStorage())
connection = psycopg2.connect(database="de5kuesnfcrulq",
                              user="dlfclsnqthaqfw",
                              password="3fd5cb1203005f2937891cec7089c8801b9e6340609eb877adc5130f9eecf4da",
                              host="ec2-34-254-69-72.eu-west-1.compute.amazonaws.com",
                              port="5432")

cursor = connection.cursor()
choses_of_actions = ['Розсилка', 'Інофрмація']
choses_of_stanucya = {'львів': -568935684,
                      'київ': -351147226,
                      'харків': -591789915,
                      'all': -544848505}

list_stanuc = ['львів','київ','харків']
class Register_state(StatesGroup):
    f_name = State()
    old = State()
    stanucya = State()
    poshta = State()


class Admin_state(StatesGroup):
    chose_of_action = State()
    chose_of_stanucya = State()
    message_to_send = State()


class Kvest_state(StatesGroup):
    start_of_quest = State()
    action_of_quest = State()
    solve_of_quest = State()
    finish_of_quest = State()

@dp.message_handler(commands=['start', 'menu'])  # cmd_start
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Зареєструватися'))
    kb.add(types.KeyboardButton('Інформація'))
    kb.add(types.KeyboardButton('Видалити реєстрацію'))
    await message.answer('''СКОБ! Друже\Подруго!''', reply_markup=kb)

@dp.message_handler(lambda message: message.text == 'Видалити реєстрацію')
async def gel_reg(message: types.Message):
    try:
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
    except psycopg2.errors.InFailedSqlTransaction:
      connection.commit()
      del_reg(message)

@dp.message_handler(lambda message: message.text == "Зареєструватися", state=None)
async def register(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT user_id FROM subs')
    data = cursor.fetchall()
    subs_ids = []
    for id in data:
        subs_ids.append(id[0])
    connection.commit()
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
    try:
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
        if "'" in f_name:
            f_name = f_name.replace("'", '')
        if user_id not in subs_ids:
            cursor.execute(f"INSERT INTO subs (username,f_name,old,user_id,stanucya,poshta,score,progress) "
                f"VALUES ('{username}', '{f_name}', '{old}', '{user_id}', '{stanucya}', '{poshta},0,0')")
            connection.commit()
        else:
            cursor.execute(f"UPDATE subs SET username='{username}',f_name='{f_name}', "
                         f"old='{old}',user_id='{user_id}',stanucya='{stanucya}', poshta='{poshta}' "
                         f"WHERE user_id={user_id}")
            connection.commit()
        await message.answer('Реєстрація Успішна')
        await state.finish()
    except psycopg2.ProgrammingError:
        connection.commit()


@dp.message_handler(lambda message: message.text == 'Інформація')
async def info(message: types.Message):
    await message.answer('''Я інтерактивний чат-бот, що стане твоїм 
    єдиним інструктором у квесті до Дня першої пластової присяги. 
    Захід буде транслюватися онлайн 11 квітня. Початок квесту: 10:00. 
    Усю потрібну інформацію відправлю тобі трохи пізніше - слідкуй за оновленнями.

Вразі виникнення проблем із ботом пропонуємо наступний алгоритм дій:
1. Перезапустити бота(введіть в чаті команду /start)
2. Не помогло? Тоді пишіть сюди: @zelenkkkaaaaa''')


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in choses_of_actions:
        kb.add(i)
    await message.answer('Привіт Адмін бота, обери дію:', reply_markup=kb)
    await Admin_state.chose_of_action.set()


@dp.message_handler(state=Admin_state.chose_of_action)
async def action(message: types.Message, state: FSMContext):
    if message.text == 'Розсилка':
        kb = types.ReplyKeyboardRemove()
        await message.answer('🖐', reply_markup=kb)
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in choses_of_stanucya.keys():
            kb.add(i)
        await message.answer('Який чат надсилаємо?', reply_markup=kb)
        await Admin_state.next()
    else:
        pass


@dp.message_handler(state=Admin_state.chose_of_stanucya)
async def choses_of_stanucya_to_send(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(chose_of_stanucya=answer)
    kb = types.ReplyKeyboardRemove()
    await message.answer('Повідомлення?', reply_markup=kb)
    await Admin_state.next()


@dp.message_handler(state=Admin_state.message_to_send)
async def message_send_to_user(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(message_to_send=text)
    cursor.execute('SELECT user_id FROM subs')
    data = cursor.fetchall()
    subs_info = []
    for id in data:
        subs_info.append(id[0])
    for i in subs_info:
        await bot.send_message(i, text)
    connection.commit()
    await state.finish()


@dp.message_handler(lambda message: message.text == "Розпочати квест")
async def solve(message: types.Message, state: FSMContext):
    await Kvest_state.start_of_quest.set()
    cursor.execute('SELECT user_id, progress FROM subs')
    data = cursor.fetchall()
    subs_info = {}
    for id, progress in data:
        subs_info[id] = progress
    user_id = message.from_user.id
    await state.update_data(action_of_quest=user_id)
    list_kb = ['Так!']
    kb = types.ReplyKeyboardMarkup()
    for i in list_kb:
        kb.add(i)
    await message.answer('Готовий розпочати квест?', reply_markup=kb)
    cursor.execute(f"UPDATE subs SET progress=1 WHERE user_id='{user_id}'")
    await Kvest_state.next()
    connection.commit()

@dp.message_handler(state=Kvest_state.action_of_quest)
async def action_of_quest(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get('action_of_quest')
    cursor.execute(f'SELECT progress FROM subs WHERE user_id={user_id}')
    data = cursor.fetchall()
    progress = data[0][0]
    for number, task in kvest.items():
        if progress == 12:
            if number == progress:
                await bot.send_photo(message.chat.id, photo=open(f'dpppBot/photos/{task[0]}', 'rb'))
                await message.answer('Напиши кілька слів відгку будь-ласка, Як тобі квест?')
                await Kvest_state.finish_of_quest.set()
                break
        if number == progress:
            if task[1] != 0:
                kb = types.InlineKeyboardMarkup(resize_keyboard=True)
                kb.add(types.InlineKeyboardButton(text='Тиць', url=f'{task[1]}'))
                await bot.send_photo(message.chat.id, photo=open(f'dpppBot/photos/{task[0]}', 'rb'), reply_markup=kb)
                await Kvest_state.next()
                break
            else:
                await bot.send_photo(message.chat.id, photo=open(f'dpppBot/photos/{task[0]}', 'rb'))
                await Kvest_state.next()
                break
        else:
            pass
    connection.commit()


@dp.message_handler(content_types=['photo', 'text'], state=Kvest_state.solve_of_quest)
async def solve_of_kvest(message: types.Message, state: FSMContext):
    id = message.message_id
    user_data = await state.get_data()
    user_id = user_data['action_of_quest']
    cursor.execute(f'SELECT stanucya FROM subs WHERE user_id={user_id}')
    data = cursor.fetchall()
    stanucya = data[0][0].replace(' ', '')
    if stanucya.lower() not in list_stanuc:
        stanucya = 'all'
    else:
        pass
    await bot.forward_message(choses_of_stanucya[f'{stanucya.lower()}'], message.chat.id, message_id=id)
    await Kvest_state.action_of_quest.set()
    cursor.execute(f'SELECT progress FROM subs WHERE user_id={user_id}')
    data = cursor.fetchall()
    current_progress = data[0][0]
    if current_progress < 12:
        cursor.execute(f'UPDATE subs SET progress={current_progress+1} WHERE user_id={user_id}')
        await message.answer('Готовий до наступного завдання?')
    else:
        await message.answer('Вітаю!')
    connection.commit()

@dp.message_handler(state=Kvest_state.finish_of_quest)
async def finish(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.forward_message(-490991329, message.chat.id, message.message_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('/start')
    await message.answer('Натисни щоб перейти в меню', reply_markup=kb)

@dp.message_handler(lambda message: 'approve' in message.text)
async def approve(message: types.Message, state: FSMContext):
    score = message.text.split(' ')[1]
    user_id = message.from_user.id
    cursor.execute(f"SELECT score FROM subs WHERE user_id = '{user_id}' ")
    data = cursor.fetchall()
    current_score = int(data[0][0])
    cursor.execute(f"UPDATE subs SET score = '{int(score) + int(current_score)}' WHERE user_id='{user_id}' ")
    await message.answer(f'Очки оновлено')
    connection.commit()


if __name__ == "__main__":  # start polling
    executor.start_polling(dp, skip_updates=True)
