import asyncio
import logging
import time
import aioschedule
import datetime
from datetime import date
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.filters.command import Command
from aiogram.filters import Filter
from aiogram.filters.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.send_message import SendMessage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy

from aiogram_dialog import DialogManager, Dialog, Window, setup_dialogs, StartMode
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.text import Format

import sqlite3

# region some important stuff

class Text(Filter): #Раньше использовалась старая версия aiogram, в которой был этот фильтр, и я к нему привык. Поэтому он теперь красуется тут, копать его-колотить(((
	def __init__(self, text: str) -> None:
		self.text = text

	async def __call__(self, message: Message | CallbackQuery) -> bool:
		try:
			res =  message.text == self.text
			#print(1,  message.text, self.text)
		except:
			res =  message.data == self.text
			#print(2,  message.data, self.text)
		
		return res
class SUPERText(Filter): #Раньше использовалась старая версия aiogram, в которой был этот фильтр, и я к нему привык. Поэтому он теперь красуется тут, копать его-колотить(((
	def __init__(self, text: str) -> None:
		self.text = text

	async def __call__(self, message: Message | CallbackQuery) -> bool:
		try:
			res = self.text in message.text
			#print(1,  message.text, self.text)
		except:
			res = self.text in message.data
			#print(2,  message.data, self.text)
		
		return res

#import mariadb
#try:
#    conn = mariadb.connect(
#        user="debservak",
#        password="figvam",
#        host="localhost",
#        database="inventosbase"
#    )
#    cur = conn.cursor()
#except mariadb.Error as e:
#    print(f"Error connecting to MariaDB Platform: {e}")
#    exit(1)

conn = sqlite3.connect('inventosbase.db')
cur = conn.cursor()
API_TOKEN = 'А ключик у бот-отца просить(((('

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

glob = {'tst': []}

class Status(StatesGroup):
	nothing = State()
	newNameForMeeting = State()
	newNameForMeetingWait = State()
	newMeetingCheck = State()
	newNotifications1 = State()
	newNotifications2 = State()
	newGuestCount = State()
	newCost = State()
	newTime = State()
	newDate = State()

	reg = State()
	regName1 = State()
	regName2 = State()

	info1 = State()
	info11 = State()
	info12 = State()

	info1cal = State()
	
	info2 = State()
	info3 = State()
	info4 = State()

	guestRegName1 = State()
	guestRegName2 = State()
	guestRegid = State()
	guestRegTelegaTag = State()
	guestRegTelegaName = State()

	guestAddidUser = State()
	guestAddidMeeting = State()

	guestRemoveidUser = State()
	guestRemoveidMeeting = State()

	redactUserName1 = State()
	redactUserName2 = State()

	redactMeeting = State()
	redactMeetingCheck = State()
	redactMeetingNameForMeetingWait = State()
	redactMeetingNotifications1 = State()
	redactMeetingNotifications2 = State()
	redactMeetingGuestCount = State()
	redactMeetingCost = State()
	redactMeetingDate = State()

	startName1 = State()
	startName2 = State()

	shareGuest = State()
	shareUser = State()
	shareID = State()

	calenka = State()
	calenka2 = State()

	adminPayId = State()
	adminPayIdUser = State()

	adminGuestIdUser = State()
	adminNewIdUser = State()
	adminUserCheck = State()

# endregion
# region start and stuff

async def isUserReg(someStuff: Message | CallbackQuery):
	idUser = someStuff.from_user.id
	cur.execute('SELECT * FROM `User` WHERE `id`=?', (int(idUser),))
	res = cur.fetchall()
	print(res, idUser)
	return res and 1

@dp.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
	parts = (message.text +  ' ').split(' ')
	if message.text == '/start':
		await message.reply("Телеграм бот для записи на мероприятие.\nПо всем попросам к @Wolchenok57.")
		if await isUserReg(message):
			cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (message.from_user.id, ))
			res = cur.fetchall()[0]
			
			name1  = res[0]
			name2  = res[1]
			idUser = int(message.from_user.id)
			cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, message.chat.id, message.from_user.full_name, message.from_user.username, idUser))
			conn.commit()
		"/start [guest|user] [callback.from_user.id-idMeeting|idMeeting]"
	elif (parts[0] + ' ' + parts[1]) == '/start guest' and len(parts)>3:
		if await isUserReg(message):
			await message.answer('Вы уже есть в системе')
			cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (message.from_user.id, ))
			res = cur.fetchall()[0]
			
			name1  = res[0]
			name2  = res[1]
			idUser = int(message.from_user.id)
			cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, message.chat.id, message.from_user.full_name, message.from_user.username, idUser))
			conn.commit()
		else:
			idUser = int(message.from_user.id)
			idChat = message.chat.id
			telega_name = message.from_user.full_name
			telega_tag = message.from_user.username

			cur.execute('INSERT INTO `User` VALUES(?, ?, ?, ?, ?, ?)', (idUser, '*Заменить*', '*Заменить*', idChat, telega_name, telega_tag))
			conn.commit()
		try:
			if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
			idUser, idMeeting = parts[2].split('-')
			cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=?;', (int(message.from_user.id), idMeeting))
			da = cur.fetchall()
			if da:
				#await message.answer('Вы успешно были записаны в очередь!')
				await notification_de_signer()
			else:
				#cur.execute('SELECT `idCreator` FROM `Meeting` WHERE `Meeting`.`id`=?;', (idMeeting, ))
				#idCreator = cur.fetchall()[0][0]
				cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (int(idMeeting), int(message.from_user.id), int(idUser), False, None, True, False))
				await notification_signer(cur.lastrowid)
				conn.commit()
			#if not da:await message.answer('Вы успешно были записаны в очередь!')
		except:
			await message.answer('Что-то пошло не так! В данный момент запись на это мероприятие невозможна.')
	
		await message.answer('Вы были приглашены! Уточните, пожалуйста некоторые данные.')
		await message.answer('Введите Ваше имя:')
		await state.set_state(Status.startName1)
		
	elif (parts[0] + ' ' + parts[1]) == '/start user' and len(parts)>3:
		if await isUserReg(message):
			await message.answer('Вы уже есть в системе')
			cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (message.from_user.id, ))
			res = cur.fetchall()[0]
			
			name1  = res[0]
			name2  = res[1]
			idUser = int(message.from_user.id)
			cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, message.chat.id, message.from_user.full_name, message.from_user.username, idUser))
			conn.commit()
		else:
			idUser = int(message.from_user.id)
			idChat = message.chat.id
			telega_name = message.from_user.full_name
			telega_tag = message.from_user.username

			cur.execute('INSERT INTO `User` VALUES(?, ?, ?, ?, ?, ?)', (idUser, '*Заменить*', '*Заменить*', idChat, telega_name, telega_tag))
			conn.commit()
		try:
			if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
			idMeeting = parts[2]
			cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=?;', (int(message.from_user.id), idMeeting))
			da = cur.fetchall()
			if da:
				#await message.answer('Вы успешно были записаны в очередь!')
				await notification_de_signer()
			else:
				cur.execute('SELECT `idCreator` FROM `Meeting` WHERE `Meeting`.`id`=?;', (idMeeting, ))
				idCreator = cur.fetchall()[0][0]
				cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (int(idMeeting), int(message.from_user.id), int(idCreator), False, None, True, False))
				await notification_signer(cur.lastrowid)
				conn.commit()
			#if not da:await message.answer('Вы успешно были записаны в очередь!')
		except:
			await message.answer('Что-то пошло не так! В данный момент запись на это мероприятие невозможна.')
	
		await message.answer('Вы были приглашены! Уточните, пожалуйста некоторые данные.')
		await message.answer('Введите Ваше имя:')
		await state.set_state(Status.startName1)
	else: await message.answer('Команда не распознана')

@dp.message(Status.startName1)
async def startName1Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="startName2"))
	await state.update_data(name1=message.text)
	await message.answer('Ваше имя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("startName2"))
async def startName2(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите Вашу фамилию:')
	await state.set_state(Status.startName2)

@dp.message(Status.startName2)
async def startName2Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="startCreate"))
	await state.update_data(name2=message.text)
	await message.answer('Ваша фамилия точно ' + str((await state.get_data())['name2']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("startCreate"))
async def startCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	#if await isUserReg(callback): await callback.message.answer('Вы уже есть в системе'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name1  = resObj['name1']
	name2  = resObj['name2']
	idUser = int(callback.from_user.id)
	#cur.execute('INSERT INTO `User` VALUES(?, ?, ?, ?, ?, ?)', (idUser, name1, name2, callback.message.chat.id, callback.from_user.full_name, callback.from_user.username))
	cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, callback.message.chat.id, callback.from_user.full_name, callback.from_user.username, idUser))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)


# endregion
# region reg

@dp.message(Command('reg'))
async def reg(message: types.Message, state: FSMContext):
	if message.text == '/reg':
		await state.clear()
		if await isUserReg(message): await message.answer('Вы уже есть в системе'); await state.set_state(Status.nothing); return 0
		txt = 'Внимание! Зайдя в этого бота вы согасились с обработкой ваших телеграммовских данных. Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Ваше имя', callback_data="regName1"))
		kbb.add(types.InlineKeyboardButton(text='Ваша фамилия', callback_data="regName2"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.reg)
	else:
		await message.answer('Команда не распознана')

@dp.callback_query(Text("regCheck"))
async def newMeetingCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	if 'name1' in data or 'name2' in data:
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		if 'name1' in data: txt += '\nВаше имя: ' + data['name1']
		else: kbb.add(types.InlineKeyboardButton(text='Ваше имя', callback_data="regName1"))
		if 'name2' in data: txt += '\nВаша фамилия: ' + data['name2']
		else: kbb.add(types.InlineKeyboardButton(text='Ваша фамилия', callback_data="regName2"))
		kbb.adjust(1, repeat=True)
		if 'name' and data and 'name2' in data:
			kbb.add(types.InlineKeyboardButton(text='Зарегистрироваться!', callback_data="regCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.newMeetingCheck)



@dp.callback_query(Text("regName1"))
async def regName1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите Ваше имя:')
	await state.set_state(Status.regName1)

@dp.message(Status.regName1)
async def regName1Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="regCheck"))
	await state.update_data(name1=message.text)
	await message.answer('Ваше имя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("regName2"))
async def regName2(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите Вашу фамилию:')
	await state.set_state(Status.regName2)

@dp.message(Status.regName2)
async def regName2Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="regCheck"))
	await state.update_data(name2=message.text)
	await message.answer('Ваша фамилия точно ' + str((await state.get_data())['name2']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("regCreate"))
async def addHumanDescription(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if await isUserReg(callback): await callback.message.answer('Вы уже есть в системе'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name1  = resObj['name1']
	name2  = resObj['name2']
	idUser = int(callback.from_user.id)
	cur.execute('INSERT INTO `User` VALUES(?, ?, ?, ?, ?, ?)', (idUser, name1, name2, callback.message.chat.id, callback.from_user.full_name, callback.from_user.username))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)

# endregion
# region new

@dp.message(Command('new'))
async def putInNew(message: types.Message, state: FSMContext):
	if message.text == '/new':
		await state.clear()
		if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Название мероприятия', callback_data="newNameForMeeting"))
		kbb.add(types.InlineKeyboardButton(text='Настроить уведомления', callback_data="newNotifications"))
		kbb.add(types.InlineKeyboardButton(text='Указать количество гостей', callback_data="newGuestCount"))
		kbb.add(types.InlineKeyboardButton(text='Указать стоимость', callback_data="newCost"))
		kbb.add(types.InlineKeyboardButton(text='Указать дату', callback_data="newDate"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.newNameForMeeting)
	else:
		await message.answer('Команда не распознана')

@dp.callback_query(Text("newMeetingCheck"))
async def newMeetingCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	if 'name' in data or 'notif' in data or 'guest' in data or 'cost' in data or 'date' in data:
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		if 'name' in data: txt += '\nНазвание: ' + data['name']
		else: kbb.add(types.InlineKeyboardButton(text='Название мероприятия', callback_data="newNameForMeeting"))
		if 'notif' in data:
			if data['notif'] == -1:
				txt += '\nУведомления отключены.'
			else:
				txt += '\nУведомление за ' + str(data['notif']) + 'минут: \n"' + str(data['notxt']) + '"'
		else: kbb.add(types.InlineKeyboardButton(text='Настроить уведомления', callback_data="newNotifications"))
		if 'guest' in data: txt += '\nКоличество гостей:' + str(data['guest'])
		else: kbb.add(types.InlineKeyboardButton(text='Указать количество гостей', callback_data="newGuestCount"))
		if 'cost' in data:
			if data['cost'] == -1:
				txt += '\nПосещение бесплатно.'
			else:
				txt += '\nСтоимость: ' + str(data['cost'])
		else: kbb.add(types.InlineKeyboardButton(text='Указать стоимость', callback_data="newCost"))
		if 'date' in data: txt += '\nДата: ' + str(data['date'].strftime('%d.%m.%y %H:%M'))
		else: kbb.add(types.InlineKeyboardButton(text='Указать дату', callback_data="newDate"))
		kbb.adjust(1, repeat=True)
		if 'name' and data and 'notif' in data and 'guest' in data and 'cost' in data and 'date' in data:
			kbb.add(types.InlineKeyboardButton(text='Создать мероприятие!', callback_data="newCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.newMeetingCheck)



@dp.callback_query(Text("newNameForMeeting"))
async def newNameForMeeting(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите название:')
	await state.set_state(Status.newNameForMeetingWait)

@dp.message(Status.newNameForMeetingWait)
async def newNameForMeetingWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newMeetingCheck"))
	await state.update_data(name=message.text)
	await message.answer('Название точно ' + str((await state.get_data())['name']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("newNotifications"))
async def newNotifications(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да', callback_data="newNotificationsAllow"))
	kbb.add(types.InlineKeyboardButton(text='Нет', callback_data="newNotificationsDisallow"))
	await callback.message.answer('Включить уведомления гостям?', reply_markup=kbb.as_markup(resize_keyboard=True))
	
@dp.callback_query(Text("newNotificationsDisallow"))
async def newNotificationsDisallow(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Уведомления отключены.')
	await state.update_data(notif=-1)
	
	await newMeetingCheck(callback, state)

@dp.callback_query(Text("newNotificationsAllow"))
async def newNotificationsAllow(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите текст уведомления:')
	await state.set_state(Status.newNotifications1)

@dp.message(Status.newNotifications1)
async def newNotificationsText(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newNotificationsCount"))
	await state.update_data(notxt=message.text)
	await message.answer('Текст точно правильный?\n' + str((await state.get_data())['notxt']) + '\nЕсли нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("newNotificationsCount"))
async def newNotificationsCountQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите интервал в минутах для уведомления:')
	
	await state.set_state(Status.newNotifications2)

@dp.message(Status.newNotifications2)
async def newNotificationsCount(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newMeetingCheck"))
		await state.update_data(notif=message.text)
		await message.answer('Правильное количество минут введено: ' + str((await state.get_data())['notif']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Минуты не опознаны, введите еще раз. Сообщение не должно содержать любых символов, кроме цифр.')



@dp.callback_query(Text("newGuestCount"))
async def newGuestCountQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите количество гостей: ')
	
	await state.set_state(Status.newGuestCount)

@dp.message(Status.newGuestCount)
async def newGuestCount(message: types.Message, state: FSMContext):
	if message.text.isdigit() and int(message.text) > 0:
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newMeetingCheck"))
		await state.update_data(guest=message.text)
		await message.answer('Максимальное количество гостей верно: ' + str((await state.get_data())['guest']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Число гостей не опознано, введите его еще раз. Оно не должно содержать любых символов, кроме цифр и быть больше 0.')



@dp.callback_query(Text("newCost"))
async def newCostQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Посещение бесплатно', callback_data="newCostFree"))
	await callback.message.answer('Введите стоимость, если посещение платное:', reply_markup=kbb.as_markup(resize_keyboard=True))
	
	await state.set_state(Status.newCost)

@dp.callback_query(Text("newCostFree"))
async def newCostFree(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Установлено бесплатное посещение.')
	await state.update_data(cost=-1)
	await newMeetingCheck(callback, state)

@dp.message(Status.newCost)
async def newCost(message: types.Message, state: FSMContext):
	isfloat = 1
	try:
		float(message.text)
	except:
		isfloat = 0
	if isfloat and float(message.text) > 0:
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newMeetingCheck"))
		await state.update_data(cost=float(message.text))
		await message.answer('Плата верна: ' + str((await state.get_data())['cost']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Число не опознано, введите его еще раз. Оно не должно содержать любых символов, кроме цифр и/или одной десятичной точки.')

@dp.callback_query(Text("newCostFree"))
async def newCostFree(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Установлено бесплатное посещение.')
	await state.update_data(cost=-1)
	await newMeetingCheck(callback, state)

# region календарь, мать его
async def choiceOfAges1(callback: CallbackQuery, widget,
						manager: DialogManager, selected_date: date):
	print('asd2')
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newTime"))
	await callback.message.answer('Дата правильная: ' + str(selected_date) + '?', reply_markup=kbb.as_markup(resize_keyboard=True))
	

	#await state.update_data(date=selected_date)
	#await state.set_state(Status.newTime)

async def choiceOfAges2(callback: CallbackQuery, widget,
						manager: DialogManager, selected_date: date):
	print('info1cal1')
	await callback.answer()
	date1 = datetime.datetime.strptime(selected_date.strftime('%d.%m.%y') + ' 00:00:00', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=0)
	date2 = datetime.datetime.strptime(selected_date.strftime('%d.%m.%y') + ' 23:59:59', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=0)
	result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
	for item in result:
		await callback.message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))

calendar = Calendar(id='calendar1', on_click = choiceOfAges1)
calendar2 = Calendar(id='calendar2', on_click = choiceOfAges2)

dialog = Dialog(Window(Format("Выберите дату:"), calendar, state=Status.calenka), 
				Window(Format("Выберите дату:"), calendar2, state=Status.calenka2))

#calendar2 = Calendar(id='calendar2', on_click = choiceOfAges2)
#dialog2 = Dialog(Window(Format("Выберите дату:"), calendar2, state=Status.calenka2))
#dp.include_router(dialog2)
#da = setup_dialogs(dp)

dp.include_router(dialog)
setup_dialogs(dp)


@dp.callback_query(Text("newDate"))#Status.newDate)
async def tst(callback: types.CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
	#await state.set_state(Status.calenka)
	await callback.answer()
	print('asd')
	await dialog_manager.start(Status.calenka)


	#await bot.answer_callback_query(callback_query_id='dadada', show_alert=False, text="Callback query was sent successfully")
	await state.set_state(Status.newDate)
# endregion
	



@dp.callback_query(Text("newTime"))
async def newTime(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	print(callback.message.text.split(':')[1][1:-1])
	await state.update_data(partdate=datetime.datetime.strptime(callback.message.text.split(':')[1][1:-1], '%Y-%m-%d'))#2023-10-26
	#print(await state.get_data())

	await callback.message.answer('Пожалуйста, введите время в формате "ЧЧ:ММ":')
	await state.set_state(Status.newTime)

@dp.message(Status.newTime)
async def newTimeWait(message: types.Message, state: FSMContext):
	#try:
		print(message.text, await state.get_data())
		#print(datetime.datetime.strptime(message.text, '%d.%m.%y %H:%M'))
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="newMeetingCheck"))
		await state.update_data(date=(await state.get_data())['partdate'] + datetime.timedelta(hours=int(message.text.split(':')[0]), minutes=int(message.text.split(':')[1])))
		await message.answer('Время правильное: ' + message.text + '?', reply_markup=kbb.as_markup(resize_keyboard=True))
	#except:
	#	await message.answer('Время не распознано. Пожалуйста, введите время в формате "ЧЧ:ММ".')

@dp.callback_query(Text("newCreate"))
async def newCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	print(callback.from_user.id, callback.message.from_user.id)
	if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name  = resObj['name']
	notif = int(resObj['notif']) if int(resObj['notif']) > 0 else 'NULL'
	notxt = resObj['notxt'] if int(resObj['notif']) > 0 else 'NULL'
	guest = int(resObj['guest'])
	cost  = int(resObj['cost'])  if resObj['cost']  > 0 else 'NULL'
	data  = resObj['date']
	cur.execute('INSERT INTO `Meeting` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)', (name, int(callback.from_user.id), notif != 'NULL', notxt, notif, guest, cost, data))
	theID = cur.lastrowid
	conn.commit()
	await callback.message.answer('Добавляю запись. Чтобы поделиться отправьте пользователю следующее сообщение.')
	await callback.message.answer('Вы приглашены на мероприятие' + str(name) + \
				'! Чтобы на него записаться, введите боту "/start user ' + str(theID) + \
				'" или, если Вы уже в системе, то "/info meeting join ' + str(theID) + '"')
	await state.set_state(Status.nothing)

# endregion
# region info

@dp.message(Command('info'))
async def info(message: types.Message, state: FSMContext):
	parts = (message.text +  ' ').split(' ')
	if message.text == '/info':
		await state.clear()
		txt = 'Для получения трубуемой информации нужно нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Список предстоящих событий', callback_data="info1"))
		kbb.add(types.InlineKeyboardButton(text='Список гостей, одобренных на определенное событие', callback_data="info2"))
		kbb.add(types.InlineKeyboardButton(text='Полный список гостей на определенное событие', callback_data="info3"))
		kbb.add(types.InlineKeyboardButton(text='Спиок Ваших гостей', callback_data="info4"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.reg)
	elif message.text == '/info queue':
		txt = 'Укажите ID события (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'
		await message.answer(txt)
		await state.set_state(Status.info2)
	elif message.text == '/info full queue':
		txt = 'Укажите ID события (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'
		await message.answer(txt)
		await state.set_state(Status.info3)
	elif message.text == '/info myguest':	
		txt = 'Укажите ID события или напишите all (все) (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'
		await message.answer(txt)
		await state.set_state(Status.info4)
	elif message.text == '/info myguest all':	
		result = await showQueue(idUser=message.from_user.id, guestOfUser=True)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	elif message.text == '/info meeting':
		txt = 'Как найти событие?'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='По дате', callback_data="info11"))
		kbb.add(types.InlineKeyboardButton(text='По создателю', callback_data="info12"))

		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.info1)
	elif (parts[0] + ' ' + parts[1] + ' ' + parts[2]) == '/info meeting join' and len(parts)>3:
		if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		try:
			if not ('-' in parts[3]):
				idMeeting = parts[3]
				cur.execute('SELECT `idCreator` FROM `Meeting` WHERE `Meeting`.`id`=?;', (idMeeting, ))
				idUser = cur.fetchall()[0][0]
			else:
				idUser, idMeeting = parts[3].split('-')
			cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=?;', (int(message.from_user.id), idMeeting))
			da = cur.fetchall()
			if da:
				await message.answer('Вы уже были записаны в очередь!')
				await notification_de_signer()
			else:
				
				cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (int(idMeeting), int(message.from_user.id), int(idUser), False, None, True, False))
				await notification_signer(cur.lastrowid)
				conn.commit()
			if not da:await message.answer('Вы успешно были записаны в очередь!')
		except:
			await message.answer('Что-то пошло не так! В данный момент запись на это мероприятие невозможна.')
	elif message.text == '/info meeting date':
		txt = 'Введите дату события в формате ДД.ММ.ГГ или нажмите на кнопку с датой:'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Сегодня', callback_data="info1Today"))
		kbb.add(types.InlineKeyboardButton(text='Завтра', callback_data="info1Tomorrow"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.info11)
	elif message.text == '/info meeting date today':
		date1 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 00:00:00', '%d.%m.%y %H:%M:%S')
		date2 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 23:59:59', '%d.%m.%y %H:%M:%S')
		result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	elif message.text == '/info meeting date tomorrow':
		date1 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 00:00:00', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=1)
		date2 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 23:59:59', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=1)
		result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	elif message.text == '/info meeting creator':
		txt = 'Введите ID, ник или тег организатора события:'
		await message.answer(txt)
		await state.set_state(Status.info12)
	elif message.text == '/info help':
		await message.answer('Cпособ получить информацию.\nИспользование: /info [что-то]\n/info - главное окно выбора\n/info queue\n/info full queue\n/info myguest\n/info myguest all\n/info meeting - окно выбора событий\n/info meeting creator - отобразить события по создателю\n/info meeting date - отобразить события по дате\n/info meeting date today - отобразить события на сегодня\n/info meeting date tomorrow - отобразить события на завтра\n/info help - вывести это сообщение')
	else:
		await message.answer('Команда не распознана')

# region functions (не команды)

async def findMeetingBetweenDates(date1, date2):
	cur.execute('SELECT `name`, `idCreator`, `allowNotification`, `notificationTime`, `notificationText`, `maxUsers`, `cost`, `date`, `id` FROM `Meeting` WHERE `date` BETWEEN ? AND ?', (str(date1), str(date2)))
	result = cur.fetchall()
	ret = []
	if not result:
		kbb = InlineKeyboardBuilder()
		txt = 'Выбранная дата не содержит событий.'
		return [(txt, kbb)]
	for meeting in result:
		#name idCreator notificationText maxUsers cost date
		print(meeting)
		
		MeetingDate = datetime.datetime.strptime(meeting[7], '%Y-%m-%d %H:%M:%S')
		txt = 	'Идентификатор события: "' + str(meeting[8]) + '"\n' + \
				'Событие "' + str(meeting[0]) + '"\n' + \
				'Время: ' + MeetingDate.strftime('%d.%m.%y %H:%M') + '\n' + \
				'Уведомления: ' + ( 'за ' + str(meeting[3]) + ' минут' if meeting[2] else 'Выключены') + '\n' + \
				('Текст уведомления: ' + str(meeting[4]) + '\n' if meeting[2] else '')  + \
				('Стоимость посещения: ' + str(meeting[6]) if meeting[6] != 'NULL' else 'Посещение бесплатное') + '\n' + \
				'Количество гостей:' + str(meeting[5])
		print(time.mktime(datetime.date.today().timetuple()), time.mktime(MeetingDate.timetuple()), MeetingDate)
		if time.time() < time.mktime(MeetingDate.timetuple()):
			kbb = InlineKeyboardBuilder()
			kbb.add(types.InlineKeyboardButton(text='Записаться на событие', callback_data="info1Sign"))
		else:
			kbb = InlineKeyboardBuilder()
		kbb.adjust(1, repeat=True)
		ret.append((txt, kbb))
	return ret

async def findMeetingByAuthor(author):
	print(author)
	cur.execute('SELECT `Meeting`.`name`, `Meeting`.`idCreator`, `Meeting`.`allowNotification`, `Meeting`.`notificationTime`, `Meeting`.`notificationText`, `Meeting`.`maxUsers`, `Meeting`.`cost`, `Meeting`.`date`, `Meeting`.`id`\
				FROM `Meeting`, `User`\
				WHERE (`User`.`id`=? OR `User`.`telega_name`=? OR `User`.`telega_tag`=?)\
				AND (`Meeting`.`idCreator`=`User`.`id`);', (str(author), str(author), str(author)))
	result = cur.fetchall()
	ret = []
	if not result:
		kbb = InlineKeyboardBuilder()
		txt = 'Выбранный пользователь не создавал событий или была допущена ошибка.'
		return [(txt, kbb)]
	for meeting in result:
		#name idCreator notificationText maxUsers cost date
		print(meeting)
		
		MeetingDate = datetime.datetime.strptime(meeting[7], '%Y-%m-%d %H:%M:%S')
		txt = 	'Идентификатор события: "' + str(meeting[8]) + '"\n' + \
				'Событие "' + str(meeting[0]) + '"\n' + \
				'Время: ' + MeetingDate.strftime('%d.%m.%y %H:%M') + '\n' + \
				'Уведомления: ' + ( 'за ' + str(meeting[3]) + ' минут' if meeting[2] else 'Выключены') + '\n' + \
				('Текст уведомления: ' + str(meeting[4]) + '\n' if meeting[2] else '')  + \
				('Стоимость посещения: ' + str(meeting[6]) if meeting[6] != 'NULL' else 'Посещение бесплатное') + '\n' + \
				'Количество гостей:' + str(meeting[5])
		print(time.mktime(datetime.date.today().timetuple()), time.mktime(MeetingDate.timetuple()), MeetingDate)
		if time.time() < time.mktime(MeetingDate.timetuple()):
			kbb = InlineKeyboardBuilder()
			kbb.add(types.InlineKeyboardButton(text='Записаться на событие', callback_data="info1Sign"))
		else:
			kbb = InlineKeyboardBuilder()
		kbb.adjust(1, repeat=True)
		ret.append((txt, kbb))
	return ret

async def showQueue(idMeeting = None, idUser = None, showAll = False, showFull = False, guestOfUser = False, onlyAttend = True, onlyPays = True):
	cur.execute('	SELECT `Queue`.`idMeeting`, `User`.`telega_name`, `User`.`telega_tag`, `User`.`id`, `Queue`.`attendStatus`, `Queue`.`payStatus`, `Meeting`.`name` \
					FROM `Queue`, `User` \
					INNER JOIN `Meeting` ON `Queue`.`idMeeting` = `Meeting`.`id` \
					WHERE ' + ('`Queue`.`idMeeting` = ? AND ' if not showAll else '') + ('`Queue`.`attendStatus` = TRUE AND ' if onlyAttend else '') + ('(`Queue`.`payStatus` = TRUE OR `Meeting`.`cost`=\'NULL\') AND ' if onlyPays else '') + '`Queue`.`idUser` = `User`.`id`' + (' AND `Queue`.`idUser` = ? ' if guestOfUser else '') + \
					'ORDER BY `Queue`.`payDate` ASC, `Queue`.`id` ASC' + \
					(' LIMIT (SELECT `maxUsers` FROM `Meeting`);' if not showFull else ''), ((idMeeting, idUser) if not showAll else (idUser, )) if guestOfUser else ((idMeeting, ) if not showAll else ()))
	result = cur.fetchall()
	cur.execute('SELECT `Meeting`.`maxUsers` FROM `Meeting` WHERE `Meeting`.`id`=?', (idMeeting, ))
	if not result:
		txt = 'Очередь пуста или неправильно указан ID события.'
		kbb = InlineKeyboardBuilder()
		return [(txt, kbb)]
	maxUsers = cur.fetchall()[0][0]
	print(maxUsers)
	ret = []
	kbb = InlineKeyboardBuilder()
	txt = 'Очередь заполнена на ' + (str(maxUsers) if len(result) > maxUsers else str(len(result))) + '/' + str(maxUsers) + '.\n Выбранный список пользователей:\n'
	for q in result:
		#`idMeeting`, `telega_name`, `telega_tag`, `User`.`id`, `attendStatus`, `payStatus`, `Meeting`.`name`
		#print(meeting)
		txt += str(q[1]) + '(@' + str(q[2]) + ', id=' + str(q[3]) + ') ' + ('посетит ' if q[4] else 'не посетит ') + str(q[4]) + ' (id=' + str(q[0]) + ').\n'
	kbb.adjust(1, repeat=True)
	ret.append((txt, kbb))
	return ret

# endregion

# region info1

@dp.callback_query(Text("info1"))
async def info1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	txt = 'Как найти событие?'
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='По дате', callback_data="info11"))
	kbb.add(types.InlineKeyboardButton(text='По создателю', callback_data="info12"))

	kbb.adjust(1, repeat=True)
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.info1)

@dp.callback_query(Text("info11"))
async def info1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	txt = 'Введите дату события в формате ДД.ММ.ГГ или нажмите на кнопку с датой:'
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Сегодня', callback_data="info1Today"))
	kbb.add(types.InlineKeyboardButton(text='Завтра', callback_data="info1Tomorrow"))
	kbb.add(types.InlineKeyboardButton(text='Открыть календарь', callback_data="info1cal"))
	kbb.adjust(1, repeat=True)
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.info11)

@dp.callback_query(Text("info1Today"))
async def info1Today(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	date1 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 00:00:00', '%d.%m.%y %H:%M:%S')
	date2 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 23:59:59', '%d.%m.%y %H:%M:%S')
	result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
	for item in result:
		await callback.message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))

@dp.callback_query(Text("info1Tomorrow"))
async def info1Tomorrow(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	date1 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 00:00:00', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=1)
	date2 = datetime.datetime.strptime(datetime.date.today().strftime('%d.%m.%y') + ' 23:59:59', '%d.%m.%y %H:%M:%S') + datetime.timedelta(days=1)
	result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
	for item in result:
		await callback.message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))




# region календарь, мать его 2

@dp.callback_query(Text("info1cal"))#Status.newDate)
async def info1cal(callback: types.CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
	#await state.set_state(Status.calenka)
	await callback.answer()
	print('info1cal2')
	await dialog_manager.start(Status.calenka2)


	#await bot.answer_callback_query(callback_query_id='dadada', show_alert=False, text="Callback query was sent successfully")
	await state.set_state(Status.info1cal)
# endregion



@dp.message(Status.info11)
async def info1Exec(message: types.Message, state: FSMContext):
	try:
		date1 = datetime.datetime.strptime(message.text + ' 00:00:00', '%d.%m.%y %H:%M:%S')
		print(date1)
		date2 = datetime.datetime.strptime(message.text + ' 23:59:59', '%d.%m.%y %H:%M:%S')
		print(date2)
		result = await findMeetingBetweenDates(date1.strftime('%Y-%m-%d %H:%M:%S'), date2.strftime('%Y-%m-%d %H:%M:%S'))
		print(result)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	except:
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Сегодня', callback_data="info1Today"))
		kbb.add(types.InlineKeyboardButton(text='Завтра', callback_data="info1Tomorrow"))
		kbb.adjust(1, repeat=True)
		await message.answer('Невозможно определить дату. Введите дату события в формате ДД.ММ.ГГ или нажмите на кнопку с датой.', reply_markup=kbb.as_markup(resize_keyboard=True))
	
@dp.callback_query(Text("info1Sign"))
async def info1Sign(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	try:
		if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		idMeeting = callback.message.text.split('"')[1]
		cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=?;', (int(callback.from_user.id), idMeeting))
		if cur.fetchall(): await callback.message.answer('Вы уже были записаны в очередь!'); return 0
		cur.execute('SELECT `idCreator` FROM `Meeting` WHERE `Meeting`.`id`=?;', (idMeeting, ))
		idCreator = cur.fetchall()[0][0]
		cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (int(idMeeting), int(callback.from_user.id), int(idCreator), False, None, True, idCreator == callback.from_user.id))
		await notification_signer(cur.lastrowid)
		conn.commit()
		await callback.message.answer('Вы успешно были записаны в очередь!')
	except:
		await callback.message.answer('Что-то пошло не так! В данный момент запись на это мероприятие невозможна.')

@dp.callback_query(Text("info12"))
async def info12(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	txt = 'Введите ID, ник или тег организатора события:'
	await callback.message.answer(txt)
	await state.set_state(Status.info12)

@dp.message(Status.info12)
async def info12Exec(message: types.Message, state: FSMContext):
	try:
		result = await findMeetingByAuthor(message.text)
		print(result)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	except:
		#kbb = InlineKeyboardBuilder()
		#kbb.add(types.InlineKeyboardButton(text='Сегодня', callback_data="info1Today"))
		#kbb.add(types.InlineKeyboardButton(text='Завтра', callback_data="info1Tomorrow"))
		#kbb.adjust(1, repeat=True)
		await message.answer('Выбранный пользователь не создавал событий или была допущена ошибка!')#, reply_markup=kbb.as_markup(resize_keyboard=True))

# endregion
# region info2

@dp.callback_query(Text("info2"))
async def info2(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	txt = 'Укажите ID события (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'

	await callback.message.answer(txt)
	await state.set_state(Status.info2)

@dp.message(Status.info2)
async def info2Exec(message: types.Message, state: FSMContext):
	#try:
		result = await showQueue(message.text)
		print(result)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	#except:
	#	await message.answer('Произошла ошибка. Проверьте правильность ID.')

# endregion
# region info3

@dp.callback_query(Text("info3"))
async def info3(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	txt = 'Укажите ID события (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'

	await callback.message.answer(txt)
	await state.set_state(Status.info3)

@dp.message(Status.info3)
async def info3Exec(message: types.Message, state: FSMContext):
	try:
		result = await showQueue(message.text, showFull=True)
		print(result)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	except:
		await message.answer('Произошла ошибка. Проверьте правильность ID.')

# endregion
# region info4

@dp.callback_query(Text("info4"))
async def info4(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	txt = 'Укажите ID события или напишите all (все) (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'

	await callback.message.answer(txt)
	await state.set_state(Status.info4)

@dp.message(Status.info4)
async def info4Exec(message: types.Message, state: FSMContext):
	try:
		if message.text == 'all' or message.text == 'все' or message.text == 'всё':
			result = await showQueue(idUser=message.from_user.id, guestOfUser=True)
		else:
			result = await showQueue(message.text, message.from_user.id, guestOfUser=True)
		print(result)
		for item in result:
			await message.answer(item[0], reply_markup=item[1].as_markup(resize_keyboard=True))
	except:
		await message.answer('Произошла ошибка. Повторите запрос позже.')

# endregion

# endregion
# region notification handler
async def notification_dealer(chat, txt):
	print('i am working')
	await bot.send_message(chat, txt)
	return aioschedule.CancelJob

async def notification_de_signer():
	await on_startup_and_daily()

async def notification_signer(idQueue):
	cur.execute(	'SELECT User.chat_id, Meeting.notificationText, Meeting.notificationTime, Meeting.date, Meeting.name \
					FROM Queue, User, Meeting  \
					WHERE Queue.id=? AND Queue.idMeeting=Meeting.id AND \
					Meeting.date > DATETIME(\'now\', \'localtime\') AND \
					strftime(\'%Y-%m-%d\', Meeting.date) = strftime(\'%Y-%m-%d\', \'now\');', (idQueue, ))
	result = cur.fetchall()
	if result: aioschedule.every().day.at((datetime.datetime.strptime(result[0][3], '%Y-%m-%d %H:%M:%S') - \
			datetime.timedelta(minutes=int(result[0][2]))).strftime('%H:%M')).do(
				notification_dealer, result[0][0], \
				'"' + str(result[0][4]) + '" - ' + datetime.datetime.strptime(result[0][3], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%y %H:%M') + ':\n' + str(result[0][1])
			)


async def notification_assigner():
	print('starting assign')
	cur.execute(	'SELECT User.chat_id, Meeting.notificationText, Meeting.notificationTime, Meeting.date, Meeting.name \
					FROM Queue, User, Meeting \
					WHERE User.id=Queue.idUser AND Queue.idMeeting=Meeting.id AND Meeting.allowNotification=TRUE AND \
					Meeting.date > DATETIME(\'now\', \'localtime\') AND strftime(\'%Y-%m-%d\', Meeting.date) = strftime(\'%Y-%m-%d\', \'now\') AND \
					(Meeting.cost IS NOT NULL AND Queue.payStatus=TRUE OR Meeting.cost IS NULL) \
			 		ORDER BY Queue.payDate ASC, Queue.id ASC \
					LIMIT (SELECT maxUsers FROM Meeting);')
	result = cur.fetchall()
	cur.execute(	'SELECT User.chat_id, Meeting.notificationTime, Meeting.date, Meeting.name \
					FROM Queue, User, Meeting \
					WHERE User.id=Queue.idUser AND Queue.idMeeting=Meeting.id AND Meeting.allowNotification=TRUE AND \
					(Meeting.idCreator=User.id OR Queue.isNewAdmin = TRUE) AND \
					Meeting.date > DATETIME(\'now\', \'localtime\') AND strftime(\'%Y-%m-%d\', Meeting.date) = strftime(\'%Y-%m-%d\', \'now\');')
	admins = cur.fetchall()
	print(result, admins)
	if not result and not admins: print('nothing to do here'); return 0
	for item in result:
		aioschedule.every().day.at((datetime.datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S') - \
			datetime.timedelta(minutes=int(item[2]))).strftime('%H:%M')).do(
				notification_dealer, item[0], \
				'"' + str(item[4]) + '" - ' + datetime.datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%y %H:%M') + ':\n' + str(item[1])
			)
	for item in admins:
		aioschedule.every().day.at((datetime.datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S') - \
			datetime.timedelta(minutes=int(item[1]))).strftime('%H:%M')).do(
				notification_dealer, item[0], \
				'Уведомления о событии "' + str(item[3]) + '" - ' + datetime.datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%y %H:%M') + ' рассылаются участникам.'
			)
	await aioschedule.run_pending()
	print('all assigned')
# endregion
# region guest

@dp.message(Command('guest'))
async def putInReg(message: types.Message, state: FSMContext):
	await state.clear()
	if message.text == '/guest':
		if not (await isUserReg(message)): await message.answer('Вы не можете приглашать гостй, пока Вы не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Чтобы увидеть ID пользователя, нужно посмотреть в информацию его профиля. Тег и ник не обязательны - гость, зайдя в бота, сможет обновить информацию сам через "/redact user autoUpdate".'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Зарегистрировать гостя', callback_data="guestRegCheck"))
		kbb.add(types.InlineKeyboardButton(text='Добавить гостя', callback_data="guestAddCheck"))
		kbb.add(types.InlineKeyboardButton(text='Удалить гостя', callback_data="guestRemoveCheck"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/guest reg':
		if not (await isUserReg(message)): await message.answer('Вы не можете приглашать гостй, пока Вы не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Чтобы увидеть ID пользователя, нужно посмотреть в информацию его профиля. Тег и ник не обязательны - гость, зайдя в бота, сможет обновить информацию сам через "/redact user autoUpdate". \nВнимание: бот не сможет первым начать диалог!'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Имя гостя', callback_data="guestRegName1"))
		kbb.add(types.InlineKeyboardButton(text='Фамилия гостя', callback_data="guestRegName2"))
		kbb.add(types.InlineKeyboardButton(text='ID гостя', callback_data="guestRegid"))
		kbb.add(types.InlineKeyboardButton(text='Тег гостя', callback_data="guestRegTelegaTag"))
		kbb.add(types.InlineKeyboardButton(text='Ник гостя', callback_data="guestRegTelegaName"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/guest add':
		if not (await isUserReg(message)): await message.answer('Вы не можете приглашать гостй, пока Вы не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Чтобы увидеть ID пользователя, нужно посмотреть в информацию его профиля. '
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Указать ID гостя', callback_data="guestAddidUser"))
		kbb.add(types.InlineKeyboardButton(text='Указать ID события', callback_data="guestAddidMeeting"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/guest remove':
		if not (await isUserReg(message)): await message.answer('Вы не можете удалять гостй, пока Вы не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Указать ID гостя', callback_data="guestRemoveidUser"))
		kbb.add(types.InlineKeyboardButton(text='Указать ID события', callback_data="guestRemoveidMeeting"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/guest help':
		await message.answer('Cпособ получить информацию.\nИспользование: /guest [что-то]\n/guest - главное окно выбора\n/guest reg - отобразить окно регистрации нового пользователя в гостевом режиме (чтобы выйти из гостевого режима потребуется, чтобы пользователь написал боту "/redact user autoUpdate")\n/guest add - добавить гостя в очередь (не более 3-х)\n/guest remove - удалить гостя из очереди\n/guest help - вывести это сообщение')
	else:
		await message.answer('Команда не распознана')

# region guest reg

@dp.callback_query(Text("guestRegCheck"))
async def guestRegCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	if 'name1' in data or 'name2' in data or 'id' in data or 'telegaTag' in data or 'telegaName' in data:
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		if 'name1' in data: txt += '\nИмя гостя: ' + data['name1']
		else: kbb.add(types.InlineKeyboardButton(text='Имя гостя', callback_data="guestRegName1"))
		if 'name2' in data: txt += '\nФамилия гостя: ' + data['name2']
		else: kbb.add(types.InlineKeyboardButton(text='Фамилия гостя', callback_data="guestRegName2"))
		if 'id' in data: txt += '\nID гостя: ' + data['id']
		else: kbb.add(types.InlineKeyboardButton(text='ID гостя', callback_data="guestRegid"))
		if 'telegaTag' in data: txt += '\nТег гостя: ' + data['telegaTag']
		else: kbb.add(types.InlineKeyboardButton(text='Тег гостя', callback_data="guestRegTelegaTag"))
		if 'telegaName' in data: txt += '\nНик гостя: ' + data['telegaName']
		else: kbb.add(types.InlineKeyboardButton(text='Ник гостя', callback_data="guestRegTelegaName"))
		kbb.adjust(1, repeat=True)
		if 'name1' and data and 'name2' in data and 'id' in data:
			kbb.add(types.InlineKeyboardButton(text='Зарегистрировать гостя!', callback_data="guestRegCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestRegName1"))
async def guestRegName1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите имя гостя:')
	await state.set_state(Status.guestRegName1)

@dp.message(Status.guestRegName1)
async def guestRegName1Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRegCheck"))
	await state.update_data(name1=message.text)
	await message.answer('Имя гостя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestRegName2"))
async def guestRegName2(callback: types.CallbackQuery, state: FSMContext):
	callback.answer()
	await callback.message.answer('Введите фамилию гостя:')
	await state.set_state(Status.guestRegName2)

@dp.message(Status.guestRegName2)
async def guestRegName2Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRegCheck"))
	await state.update_data(name2=message.text)
	await message.answer('Фамилия гостя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestRegid"))
async def guestRegid(callback: types.CallbackQuery, state: FSMContext):
	callback.answer()
	await callback.message.answer('Введите ID гостя:')
	await state.set_state(Status.guestRegid)
	callback.answer()

@dp.message(Status.guestRegid)
async def guestRegidWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRegCheck"))
	await state.update_data(id=message.text)
	await message.answer('ID гостя точно ' + str((await state.get_data())['id']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestRegTelegaTag"))
async def guestRegTelegaTag(callback: types.CallbackQuery, state: FSMContext):
	callback.answer()
	await callback.message.answer('Введите тег гостя:')
	await state.set_state(Status.guestRegTelegaTag)
	callback.answer()

@dp.message(Status.guestRegTelegaTag)
async def guestRegTelegaTagWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRegCheck"))
	await state.update_data(telegaTag=message.text)
	await message.answer('Тег гостя точно ' + str((await state.get_data())['telegaTag']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestRegTelegaName"))
async def guestRegTelegaName(callback: types.CallbackQuery, state: FSMContext):
	callback.answer()
	await callback.message.answer('Введите ник гостя:')
	await state.set_state(Status.guestRegTelegaName)
	callback.answer()

@dp.message(Status.guestRegTelegaName)
async def guestRegTelegaNameWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRegCheck"))
	await state.update_data(telegaName=message.text)
	await message.answer('Ник гостя точно ' + str((await state.get_data())['telegaName']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestRegCreate"))
async def guestRegCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if await isUserReg(callback): await callback.message.answer('Вы уже есть в системе'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name1  = resObj['name1']
	name2  = resObj['name2']
	full_name = resObj['telegaName']
	username = resObj['telegaTag']
	idUser = resObj['id']
	cur.execute('INSERT INTO `User` VALUES(?, ?, ?, ?, ?, ?)', (idUser, name1, name2, idUser, full_name, username))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)

# endregion
# region guest add
@dp.callback_query(Text("guestAddCheck"))
async def guestAddCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	if 'name1' in data or 'name2' in data or 'id' in data or 'telegaTag' in data or 'telegaName' in data:
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		if 'idUser' in data: txt += '\ID гостя: ' + data['idUser']
		else: kbb.add(types.InlineKeyboardButton(text='Указать ID гостя', callback_data="guestAddidUser"))
		if 'idMeeting' in data: txt += '\nИмя гостя: ' + data['idMeeting']
		else: kbb.add(types.InlineKeyboardButton(text='Указать ID события', callback_data="guestAddidMeeting"))
		kbb.adjust(1, repeat=True)
		if 'name1' and data and 'name2' in data and 'id' in data:
			kbb.add(types.InlineKeyboardButton(text='Зарегистрировать гостя!', callback_data="guestAddCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestAddidUser"))
async def guestAddidUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID гостя:')
	await state.set_state(Status.guestAddidUser)

@dp.message(Status.guestAddidUser)
async def guestAddidUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestAddCheck"))
	await state.update_data(name1=message.text)
	await message.answer('ID гостя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestAddidMeeting"))
async def guestRegName1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID события (узнать id события можно в "/info meeting" или в /info, нажав нужную кнопку):')
	await state.set_state(Status.guestAddidMeeting)

@dp.message(Status.guestAddidMeeting)
async def guestAddidMeetingWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestAddCheck"))
	await state.update_data(name1=message.text)
	await message.answer('ID события точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestAddCreate"))
async def guestAddCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	try:
		if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		resObj = await state.get_data()
		idMeeting = int(resObj['idMeeting']) if 'idMeeting' in resObj else 'NULL'
		idUser = int(resObj['idUser']) if 'idUser' in resObj else 'NULL'
		myID = callback.from_user.id
		cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`guestOf`=? AND `Queue`.`idMeeting`=?;', (myID, idMeeting))
		if len(cur.fetchall()) > 3: await callback.message.answer('Превышено количество гостей!'); return 0
		cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=?;', (idUser, idMeeting))
		if cur.fetchall(): await callback.message.answer('Ваш гость уже был записан в очередь!'); return 0
		cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (int(idMeeting), int(idUser), int(myID), False, None, True, False))
		await notification_signer(cur.lastrowid)
		conn.commit()
		await callback.message.answer('Гость успешно был записан в очередь!')
		await state.set_state(Status.nothing)
	except:
		await callback.message.answer('Что-то пошло не так, попробуйте позже.')
		return 0

# endregion
# region guest remove
@dp.callback_query(Text("guestRemoveCheck"))
async def guestAddCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	if 'name1' in data or 'name2' in data or 'id' in data or 'telegaTag' in data or 'telegaName' in data:
		txt = 'Для добавления информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		if 'idUser' in data: txt += '\ID гостя: ' + data['idUser']
		else: kbb.add(types.InlineKeyboardButton(text='Указать ID гостя', callback_data="guestRemoveidUser"))
		if 'idMeeting' in data: txt += '\nИмя гостя: ' + data['idMeeting']
		else: kbb.add(types.InlineKeyboardButton(text='Указать ID события', callback_data="guestRemoveidMeeting"))
		kbb.adjust(1, repeat=True)
		if 'name1' and data and 'name2' in data and 'id' in data:
			kbb.add(types.InlineKeyboardButton(text='Убрать гостя из очереди', callback_data="guestRemoveCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestRemoveidUser"))
async def guestRemoveidUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID гостя:')
	await state.set_state(Status.guestRemoveidUser)

@dp.message(Status.guestRemoveidUser)
async def guestRemoveidUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRemoveCheck"))
	await state.update_data(name1=message.text)
	await message.answer('ID гостя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("guestRemoveidMeeting"))
async def guestRemoveidMeeting(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID события (узнать id события можно в "/info meeting" или в /info, нажав нужную кнопку):')
	await state.set_state(Status.guestRemoveidMeeting)

@dp.message(Status.guestRemoveidMeeting)
async def guestRemoveidMeetingWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="guestRemoveCheck"))
	await state.update_data(name1=message.text)
	await message.answer('ID события точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("guestRemoveCreate"))
async def guestRemoveCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	try:
		if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		resObj = await state.get_data()
		idMeeting = int(resObj['idMeeting']) if 'idMeeting' in resObj else 'NULL'
		idUser = int(resObj['idUser']) if 'idUser' in resObj else 'NULL'
		myID = callback.from_user.id
		cur.execute('SELECT `idUser` FROM `Queue` WHERE `Queue`.`idUser`=? AND `Queue`.`idMeeting`=? AND guestOf=?;', (idUser, idMeeting, int(myID)))
		if not cur.fetchall(): await callback.message.answer('Этого гостя уже нет в очереди (или это не Ваш гость)!'); return 0
		cur.execute('DELETE FROM `Queue` WHERE idMeeting=? AND idUser=? AND guestOf=?;', (int(idMeeting), int(idUser), int(myID)))
		conn.commit()
		await notification_de_signer()
		await callback.message.answer('Гость успешно был убран из очереди!')
		await state.set_state(Status.nothing)
	except:
		await callback.message.answer('Что-то пошло не так, попробуйте позже.')
		return 0

# endregion

# endregion
# region whoami

@dp.message(Command('whoami'))
async def whoami(message: types.Message, state: FSMContext):
	if message.text == '/whoami':
		txt = 'Общая информация о пользователе.\n'
		if not await isUserReg(message): await message.answer('Вас пока нет в системе'); return 0
		idUser = message.from_user.id
		cur.execute('	SELECT name1, name2, id, telega_name, telega_tag \
						FROM User \
						WHERE id=?;', (int(idUser),))
		userInfo = cur.fetchall()[0]
		txt += 'Имя: ' + str(userInfo[0]) + '\n'
		txt += 'Фамилия: ' + str(userInfo[1]) + '\n'
		txt += 'ID: ' + str(userInfo[2]) + '\n'
		txt += 'Ник в телеге: ' + str(userInfo[3]) + '\n'
		txt += 'Тег в телеге: ' + str(userInfo[4]) + '\n'


		cur.execute('	SELECT Meeting.name, Meeting.id, Meeting.date, Queue.attendStatus, Meeting.cost, Queue.payStatus, Queue.isNewAdmin \
						FROM Meeting, Queue \
						WHERE Queue.idUser=? AND Meeting.id=Queue.idMeeting AND Meeting.date > DATETIME(\'now\', \'localtime\');', (int(idUser),))
		queueInfo = cur.fetchall()
		cur.execute('	SELECT Meeting.name, Meeting.id, Meeting.date \
						FROM Meeting \
						WHERE Meeting.idCreator=?;', (int(idUser),))
		hostInfo = cur.fetchall()
		if len(queueInfo): txt += 'Список предстоящих событий, на которое вы можете попасть:'
		for item in queueInfo:
			txt += '\n"' + str(item[0]) + '" (' + str(item[1]) + ') ' + str(item[2]) + ' ; Приглашение ' + ('принято' if bool(item[3]) else 'отклонено') + ((' и оплачено' if bool(item[4]) and bool(item[5]) else (' и не оплачено' if bool(item[4]) else '')) + (' (администратор)' if bool(item[6]) else ''))
		if len(hostInfo): txt += '\nСписок Ваших событий:'
		for item in hostInfo:
			txt += '\n"' + str(item[0]) + '" (' + str(item[1]) + ') ' + str(item[2])
			

		await message.answer(txt)
	else:
		await message.answer('Команда не распознана')
# endregion
# region redact

@dp.message(Command('redact'))
async def redact(message: types.Message, state: FSMContext):
	if message.text == '/redact':
		await state.clear()
		if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
		txt = 'Для изменения информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Изменить свою информацию', callback_data="redactUser"))
		kbb.add(types.InlineKeyboardButton(text='Изменить мероприятие', callback_data="redactMeeting"))
		kbb.add(types.InlineKeyboardButton(text='Управление посещением', callback_data="redactQueue"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/redact user':
		cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (message.from_user.id, ))
		res = cur.fetchall()[0]
		await state.update_data(name1=res[0])
		await state.update_data(name2=res[1])

		txt = 'Для изменения информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		txt += '\nВаше имя: ' + res[0]
		kbb.add(types.InlineKeyboardButton(text='Изменить имя', callback_data="redactUserName1"))
		txt += '\nВаша фамилия: ' + res[1]
		kbb.add(types.InlineKeyboardButton(text='Изменить фамилию', callback_data="redactUserName2"))
		kbb.adjust(2, 1, repeat=True)
		kbb.add(types.InlineKeyboardButton(text='Применить', callback_data="redactUserCreate"))
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	elif message.text == '/redact user autoUpdate':
		if await isUserReg(message): await message.answer('Вас еще нет в системе. Зарегисироваться /reg'); await state.set_state(Status.nothing); return 0
		cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (message.from_user.id, ))
		res = cur.fetchall()[0]
		name1  = res[0]
		name2  = res[1]
		idUser = int(message.from_user.id)
		cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, message.chat.id, message.from_user.full_name, message.from_user.username, idUser))
		conn.commit()
		await message.answer('Добавляю запись.')
		await state.set_state(Status.nothing)
	elif message.text == '/redact help':
		await message.answer('Cпособ редактировать информацию.\nИспользование: /redact [что-то]\n/redact - главное окно выбора\n/redact meeting - изменить существующее мероприятие\n/redact user - изменить свои данные\n/redact user autoUpdate - автоматически обновить чат (например, для перехода из личного в групповой и наоборот), тег и ник при их изменении (отсутствии)\n/redact help - вывести это сообщение')
	else:
		await message.answer('Команда не распознана')


# region redact user
@dp.callback_query(Text("redactUser"))
async def redactUserCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	if not 'name1' in data:
		cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (callback.from_user.id, ))
		res = cur.fetchall()[0]
		await state.update_data(name1=res[0])
		await state.update_data(name2=res[1])
		data = await state.get_data()

	txt = 'Ошибка. Начните операцию заново.'
	if 'name1' in data or 'name2' in data:
		txt = 'Для изменения информации нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		txt += '\nВаше имя: ' + data['name1']
		kbb.add(types.InlineKeyboardButton(text='Изменить имя', callback_data="redactUserName1"))
		txt += '\nВаша фамилия: ' + data['name2']
		kbb.add(types.InlineKeyboardButton(text='Изменить фамилию', callback_data="redactUserName2"))
		kbb.add(types.InlineKeyboardButton(text='Применить', callback_data="redactUserCreate"))
		kbb.adjust(2, 1, repeat=True)
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("redactUserName1"))
async def redactUserName1(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите Ваше имя:')
	await state.set_state(Status.redactUserName1)

@dp.message(Status.redactUserName1)
async def redactUserName1Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactUser"))
	await state.update_data(name1=message.text)
	await message.answer('Ваше имя точно ' + str((await state.get_data())['name1']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("redactUserName2"))
async def redactUserName2(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите Вашу фамилию:')
	await state.set_state(Status.redactUserName2)

@dp.message(Status.redactUserName2)
async def redactUserName2Wait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactUser"))
	await state.update_data(name2=message.text)
	await message.answer('Ваша фамилия точно ' + str((await state.get_data())['name2']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("redactUserCreate"))
async def redactUserCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if not await isUserReg(callback): await callback.message.answer('Вас нет в системе. Зарегистрироваться /reg'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name1  = resObj['name1']
	name2  = resObj['name2']
	idUser = int(callback.from_user.id)
	cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, callback.message.chat.id, callback.from_user.full_name, callback.from_user.username, idUser))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)
# endregion
# region redact user autoUpdate
@dp.callback_query(Text("redactUserAutoUpdate"))
async def redactUserAutoUpdateCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if not (await isUserReg(callback)): await callback.message.answer('Вас еще нет в системе. Зарегисироваться /reg'); await state.set_state(Status.nothing); return 0

	cur.execute('SELECT `name1`, `name2` FROM `User` WHERE `id`=?;', (callback.from_user.id, ))
	res = cur.fetchall()[0]
	
	name1  = res[0]
	name2  = res[1]
	idUser = int(callback.from_user.id)
	cur.execute('UPDATE `User` SET `name1`=?, `name2`=?, `chat_id`=?, `telega_name`=?, `telega_tag`=? WHERE `id`=?;', (name1, name2, callback.message.chat.id, callback.from_user.full_name, callback.from_user.username, idUser))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)
# endregion
# region redact meeting

@dp.callback_query(Text("redactMeeting"))
async def redactMeeting(callback: types.CallbackQuery, state: FSMContext):
	await state.clear()
	if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	txt = 'Укажите ID события (событие можно найти в "/info meeting" или нажав на кнопку "Список предстоящих событий" в /info):'
	await callback.message.answer(txt)
	await state.set_state(Status.redactMeeting)

@dp.message(Status.redactMeeting)
async def redactMeetingWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
	await state.update_data(id=message.text)
	await message.answer('ID точно ' + str((await state.get_data())['id']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))


@dp.callback_query(Text("redactMeetingCheck"))
async def redactMeetingCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	data = await state.get_data()
	if not 'name1' in data:
		cur.execute('SELECT `name`, `allowNotification`, `notificationText`, `notificationTime`, `maxUsers`, `cost`, `date` FROM `Meeting` WHERE `id`=?;', (data['id'], ))
		res = cur.fetchall()[0]
		await state.update_data(name=res[0])
		await state.update_data(allowNotification=res[1])
		await state.update_data(notificationText=res[2])
		await state.update_data(notificationTime=res[3])
		await state.update_data(maxUsers=res[4])
		await state.update_data(cost=res[5])
		await state.update_data(date=res[6])
		data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	print(data, 'notif' in data)
	
	txt = 'Для изменения информации нажать кнопки снизу.'
	kbb = InlineKeyboardBuilder()
	txt += '\nНазвание: ' + data['name']
	kbb.add(types.InlineKeyboardButton(text='Название мероприятия', callback_data="redactMeetingNameForMeeting"))
	if data['notif'] == -1 or data['notif'] == 'NULL':
		txt += '\nУведомления отключены.'
	else:
		txt += '\nУведомление за ' + str(data['notif']) + 'минут: \n"' + str(data['notxt']) + '"'
	kbb.add(types.InlineKeyboardButton(text='Настроить уведомления', callback_data="redactMeetingNotifications"))
	txt += '\nКоличество гостей:' + str(data['guest'])
	kbb.add(types.InlineKeyboardButton(text='Указать количество гостей', callback_data="redactMeetingGuestCount"))
	
	if data['cost'] == -1 or data['cost'] == 'NULL':
		txt += '\nПосещение бесплатно.'
	else:
		txt += '\nСтоимость: ' + str(data['cost'])
	kbb.add(types.InlineKeyboardButton(text='Указать стоимость', callback_data="redactMeetingCost"))
	txt += '\nДата: ' + str(data['date'].strftime('%d.%m.%y %H:%M'))
	kbb.add(types.InlineKeyboardButton(text='Указать дату', callback_data="redactMeetingDate"))
	kbb.adjust(1, repeat=True)
	kbb.add(types.InlineKeyboardButton(text='Применить!', callback_data="redactMeetingCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.redactMeetingCheck)



@dp.callback_query(Text("redactMeetingNameForMeeting"))
async def redactMeetingNameForMeeting(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите название:')
	await state.set_state(Status.redactMeetingNameForMeetingWait)

@dp.message(Status.redactMeetingNameForMeetingWait)
async def redactMeetingNameForMeetingWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
	await state.update_data(name=message.text)
	await message.answer('Название точно ' + str((await state.get_data())['name']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("redactMeetingNotifications"))
async def redactMeetingNotifications(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да', callback_data="redactMeetingNotificationsAllow"))
	kbb.add(types.InlineKeyboardButton(text='Нет', callback_data="redactMeetingNotificationsDisallow"))
	await callback.message.answer('Включить уведомления гостям?', reply_markup=kbb.as_markup(resize_keyboard=True))
	
@dp.callback_query(Text("redactMeetingNotificationsDisallow"))
async def redactMeetingNotificationsDisallow(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Уведомления отключены.')
	await state.update_data(notif=-1)
	
	await redactMeetingCheck(callback, state)

@dp.callback_query(Text("redactMeetingNotificationsAllow"))
async def redactMeetingNotificationsAllow(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите текст уведомления:')
	await state.set_state(Status.redactMeetingNotifications1)

@dp.message(Status.redactMeetingNotifications1)
async def redactMeetingNotificationsText(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingNotificationsCount"))
	await state.update_data(notxt=message.text)
	await message.answer('Текст точно правильный?\n' + str((await state.get_data())['notxt']) + '\nЕсли нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("redactMeetingNotificationsCount"))
async def redactMeetingNotificationsCountQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите интервал в минутах для уведомления:')
	
	await state.set_state(Status.redactMeetingNotifications2)

@dp.message(Status.redactMeetingNotifications2)
async def redactMeetingNotificationsCount(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
		await state.update_data(notif=message.text)
		await message.answer('Правильное количество минут введено: ' + str((await state.get_data())['notif']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Минуты не опознаны, введите еще раз. Сообщение не должно содержать любых символов, кроме цифр.')



@dp.callback_query(Text("redactMeetingGuestCount"))
async def redactMeetingGuestCountQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите количество гостей: ')
	
	await state.set_state(Status.redactMeetingGuestCount)

@dp.message(Status.redactMeetingGuestCount)
async def redactMeetingGuestCount(message: types.Message, state: FSMContext):
	if message.text.isdigit() and int(message.text) > 0:
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
		await state.update_data(guest=message.text)
		await message.answer('Максимальное количество гостей верно: ' + str((await state.get_data())['guest']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Число гостей не опознано, введите его еще раз. Оно не должно содержать любых символов, кроме цифр и быть больше 0.')



@dp.callback_query(Text("redactMeetingCost"))
async def redactMeetingCostQuestion(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Посещение бесплатно', callback_data="redactMeetingCostFree"))
	await callback.message.answer('Введите стоимость, если посещение платное:', reply_markup=kbb.as_markup(resize_keyboard=True))
	
	await state.set_state(Status.redactMeetingCost)

@dp.callback_query(Text("redactMeetingCostFree"))
async def redactMeetingCostFree(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Установлено бесплатное посещение.')
	await state.update_data(cost=-1)
	await redactMeetingCheck(callback, state)

@dp.message(Status.redactMeetingCost)
async def redactMeetingCost(message: types.Message, state: FSMContext):
	isfloat = 1
	try:
		float(message.text)
	except:
		isfloat = 0
	if isfloat and float(message.text) > 0:
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
		await state.update_data(cost=float(message.text))
		await message.answer('Плата верна: ' + str((await state.get_data())['cost']) + '? Если нет, введите его еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Число не опознано, введите его еще раз. Оно не должно содержать любых символов, кроме цифр и/или одной десятичной точки.')

@dp.callback_query(Text("redactMeetingCostFree"))
async def redactMeetingCostFree(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Установлено бесплатное посещение.')
	await state.update_data(cost=-1)
	await redactMeetingCheck(callback, state)



@dp.callback_query(Text("redactMeetingDate"))
async def redactMeetingDate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Пожалуйста, введите дату в формате "ДД.ММ.ГГ ЧЧ:ММ":')

	await state.set_state(Status.redactMeetingDate)

@dp.message(Status.redactMeetingDate)
async def redactMeetingCost(message: types.Message, state: FSMContext):
	try:
		print(message.text)
		print(datetime.datetime.strptime(message.text, '%d.%m.%y %H:%M'))
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="redactMeetingCheck"))
		await state.update_data(date=datetime.datetime.strptime(message.text, '%d.%m.%y %H:%M'))
		await message.answer('Дата правильная: ' + message.text + '?', reply_markup=kbb.as_markup(resize_keyboard=True))
	except:
		await message.answer('Дата не распознана. Пожалуйста, введите дату в формате "ДД.ММ.ГГ ЧЧ:ММ:CC".')

@dp.callback_query(Text("redactMeetingCreate"))
async def redactMeetingCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	print(callback.from_user.id, callback.message.from_user.id)
	if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name  = resObj['name']
	notif = int(resObj['notif']) if int(resObj['notif']) > 0 else 'NULL'
	notxt = resObj['notxt'] if int(resObj['notif']) > 0 else 'NULL'
	guest = int(resObj['guest'])
	cost  = int(resObj['cost'])  if resObj['cost']  > 0 else 'NULL'
	data  = resObj['date']
	idMeeting = resObj['id']
	#cur.execute('INSERT INTO `Meeting` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)', (name, int(callback.from_user.id), notif != 'NULL', notxt, notif, guest, cost, data))
	cur.execute('UPDATE `Meeting` SET `name`=?, `idCreator`=?, `allowNotification`=?, `notificationText`=?, `notificationTime`=?, `maxUsers`=?, `cost`=?, `date`=? WHERE `id`=?;', (name, int(callback.from_user.id), notif != 'NULL', notxt, notif, guest, cost, data, idMeeting))
	conn.commit()

	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)

# endregion

# endregion
# region help



@dp.message(Command('help'))
async def send_welcome(message: types.Message):
	if message.text == '/help':
		await message.answer(#надоело!!!! Хочу уже все это закончиьтьь не хотю расставлять переносы строк и делать грустную длинную строку((((
'''В этом сообщении, рзъясняющются значения команд этого бота.
Список доступных команд:
/reg - регистрация нового пользователя в системе
/new - создание нового события
/info - отобразить различную информацию (здесь также происходит запись на события)
/guest - управление гостями
/whoami - отображение хранимой личной телеграммовской информации о пользователе
/redact - редактировать или обновить личную информацию
/help - показать сообщение, рзъясняющее значение команд этого бота
/ping - отладочная команда, в которой отображается вся информация, доступная боту из каждого сообщения, отправленного пользователем
Каждая команда, которая содержит несколько выборов, также имеет некоторые нестандартные способы использования. Если таковой есть, можно ввести /ping help, где ping нужно заменить на требуемую команду.''')
	if message.text == '/help help':
		await message.answer('Простой способ получить отладочную информацию.\n\
					   usage: /help [help]\n\
					   /help - показать справку по основным командам бота\n\
					   /help help - вывести это сообщение')
		
# endregion

# region share

@dp.message(Command('share'))
async def share(message: types.Message, state: FSMContext):
	parts = (message.text +  ' ').split(' ')
	if message.text == '/share':
		await state.clear()
		txt = 'Для получения трубуемой информации нужно нажать кнопки снизу. Если вы делитесь своим событием, используйте только второй вариант.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Пригласить как Вашего гостя (3 на событие максимум)', callback_data="shareGuest"))
		kbb.add(types.InlineKeyboardButton(text='Пригласить как простого пользователя', callback_data="shareUser"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
		await state.set_state(Status.share)

	elif (parts[0] + ' ' + parts[1]) == '/share guest' and len(parts)>3:
		name = ' '.join(parts[3:-1])
		await message.answer('Чтобы поделиться отправьте пользователю следующее сообщение.')
		await message.answer('Вы приглашены на мероприятие' + (' ' + name if name else '') + '! Чтобы на него записаться, введите боту "/start guest ' + str(message.from_user.id) + '-' + parts[2] + '" или, если Вы уже в системе, то "/info meeting join ' + str(message.from_user.id) + '-' + parts[2] + '"')
	elif (parts[0] + ' ' + parts[1]) == '/share user' and len(parts)>3:
		name = ' '.join(parts[3:-1])
		await message.answer('Чтобы поделиться отправьте пользователю следующее сообщение.')
		await message.answer('Вы приглашены на мероприятие' + (' ' + name if name else '') + '! Чтобы на него записаться, введите боту "/start user ' + parts[2] + '" или, если Вы уже в системе, то "/info meeting join ' + parts[2] + '"')
	
	else:
		await message.answer('Команда не распознана')

@dp.callback_query(Text("shareGuest"))
async def shareGuest(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID события:')
	await state.set_state(Status.shareGuest)

@dp.message(Status.shareGuest)
async def shareGuestWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="shareID"))
	await state.update_data(idMeeting=message.text)
	await state.update_data(isGuest=True)
	await message.answer('ID события точно ' + str((await state.get_data())['idMeeting']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("shareUser"))
async def shareUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID события (его можно узнать в /info):')
	await state.set_state(Status.shareUser)

@dp.message(Status.shareUser)
async def shareUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="shareID"))
	await state.update_data(idMeeting=message.text)
	await state.update_data(isGuest=False)
	await message.answer('ID события точно ' + str((await state.get_data())['idMeeting']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("shareID"))
async def shareID(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID события (его можно узнать в /info):')
	await state.set_state(Status.shareID)

@dp.message(Status.shareID)
async def shareIDWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="shareCreate"))
	await state.update_data(idMeeting=message.text)
	await state.update_data(isGuest=False)
	await message.answer('ID события точно ' + str((await state.get_data())['idMeeting']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("shareCreate"))
async def shareCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	print(callback.from_user.id, callback.message.from_user.id)
	if not (await isUserReg(callback)): await callback.message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	resObj = await state.get_data()
	name  = resObj['name']
	isGuest  = resObj['isGuest']
	idMeeting  = resObj['idMeeting']
	await callback.message.answer('Чтобы поделиться отправьте пользователю следующее сообщение.')
	await callback.message.answer('Вы приглашены на мероприятие "' + name + '"! Чтобы на него записаться, введите боту "/start ' + ('guest ' + str(callback.from_user.id) + '-' if isGuest else 'user ') + idMeeting + '" или, если Вы уже в системе, то "/info meeting join ' + (str(callback.from_user.id) + '-' if isGuest else '') + idMeeting + '"')
	await state.set_state(Status.nothing)
		
# endregion

# region admin

@dp.message(Command('admin'))
async def admin(message: types.Message, state: FSMContext):
	if not (await isUserReg(message)): await message.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	await state.clear()
	parts = (message.text +  ' ').split(' ')
	if message.text == '/admin':
		txt = 'Для выбора нажать кнопки снизу.'
		kbb = InlineKeyboardBuilder()
		kbb.add(types.InlineKeyboardButton(text='Контроль оплаты', callback_data="adminPayCheck"))
		kbb.add(types.InlineKeyboardButton(text='Исключить гостя', callback_data="adminGuestCheck"))
		kbb.add(types.InlineKeyboardButton(text='Новый администратор', callback_data="adminNewCheck"))
		kbb.add(types.InlineKeyboardButton(text='Получить ID пользователя', callback_data="adminUserCheck"))
		kbb.add(types.InlineKeyboardButton(text='Администрируемые события', callback_data="adminList"))
		kbb.adjust(1, repeat=True)
		await message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	else:
		await message.answer('Команда не распознана')

# region adminPay

@dp.callback_query(Text("adminPayCheck"))
async def adminPayCheck(callback: types.CallbackQuery, state: FSMContext):
	if not (await isUserReg(callback)): await callback.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	await callback.answer()
	data = await state.get_data()
	txt = 'Ошибка. Начните операцию заново.'
	if not ('status' in data) and 'idUser' in data and 'id' in data:
		cur.execute('SELECT payStatus FROM Queue WHERE idUser=? AND idMeeting=?;', (data['idUser'], data['id']))
		res = cur.fetchall()
		if res:
			await state.update_data(status='Оплачено' if bool(res[0][0]) else 'Не оплачено')
			data = await state.get_data()
		else:
			await state.update_data(status='Не посетит событие')
	kbb = InlineKeyboardBuilder()
	txt = 'Для добавления информации нажать кнопки снизу.'
	if 'id' in data: txt += '\nID события: ' + str(data['id'])
	else: kbb.add(types.InlineKeyboardButton(text='ID события', callback_data="adminPayId"))
	if 'idUser' in data: txt += '\nID пользователя: ' + str(data['idUser'])
	else: kbb.add(types.InlineKeyboardButton(text='ID пользователя', callback_data="adminPayIdUser"))
	if 'status' in data: txt += '\nСтатус оплаты: ' + str(data['status'])
	kbb.add(types.InlineKeyboardButton(text='Статус оплаты', callback_data="adminPayStatus"))
	kbb.adjust(1, repeat=True)
	if 'id' and data and 'idUser' in data and 'status' in data and data['status'] != 'Не посетит событие':
		kbb.add(types.InlineKeyboardButton(text='Подтвердить!', callback_data="adminPayCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.newMeetingCheck)



@dp.callback_query(Text("adminPayId"))
async def adminPayId(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('	SELECT Meeting.id, Meeting.name \
					FROM Queue \
					JOIN Meeting ON Queue.idMeeting = Meeting.id \
					WHERE ((Queue.idUser = ? AND Queue.isNewAdmin = TRUE) \
					OR Meeting.idCreator = ?) \
					AND Meeting.date > DATETIME(\'now\', \'localtime\');', (callback.from_user.id, callback.from_user.id))
	res = cur.fetchall()
	if not res: await callback.message.answer('На данный момент нет предстоящих событий, в которых Вы администратор.'); return 0
	kbb = InlineKeyboardBuilder()
	for item in res:
		kbb.add(types.InlineKeyboardButton(text='' + item[1], callback_data="adminPayId " + str(item[0])))
	#await state.update_data(id=message.text)
	await callback.message.answer('Выберите событие:', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(SUPERText("adminPayId "))
async def adminPayIdChoise(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('SELECT name FROM Meeting WHERE id=?;', (callback.data.split(' ')[1], ))
	await callback.message.answer('Выбрано событие ' + cur.fetchall()[0][0])
	await state.update_data(id=int(callback.data.split(' ')[1]))
	
	await adminPayCheck(callback, state)

@dp.callback_query(Text("adminPayIdUser"))
async def adminPayIdUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID пользователя:')
	await state.set_state(Status.adminPayIdUser)

@dp.message(Status.adminPayIdUser)
async def adminPayIdUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="adminPayCheck"))
	await state.update_data(idUser=message.text)
	await message.answer('ID пользователя точно ' + str((await state.get_data())['idUser']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("adminPayStatus"))
async def adminPayStatus(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Оплатил', callback_data="adminPayStatusTrue"))
	kbb.add(types.InlineKeyboardButton(text='Не оплатил', callback_data="adminPayStatusFalse"))
	await callback.message.answer('Выберите статус оплаты:', reply_markup=kbb.as_markup(resize_keyboard=True))
@dp.callback_query(Text("adminPayStatusTrue"))
async def adminPayStatusTrue(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await state.update_data(status='Оплачено')
	await adminPayCheck(callback, state)
@dp.callback_query(Text("adminPayStatusFalse"))
async def adminPayStatusFalse(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await state.update_data(status='Не оплачено')
	await adminPayCheck(callback, state)
	


@dp.callback_query(Text("adminPayCreate"))
async def adminPayCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if not (await isUserReg(callback)): await callback.message.answer('Вас еще нет в системе. Зарегисироваться /reg'); await state.set_state(Status.nothing); return 0
	
	data = await state.get_data()
	idMeeting  = data['id']
	idUser  = data['idUser']
	status  = True if data['status'] == 'Оплачено' else False

	cur.execute('UPDATE `Queue` SET `payStatus`=?, `payDate`=DATETIME(\'now\', \'localtime\') WHERE `idMeeting`=? AND idUser=?;', (status, idMeeting, idUser))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)

# endregion
# region adminGuest

@dp.callback_query(Text("adminGuestCheck"))
async def adminGuestCheck(callback: types.CallbackQuery, state: FSMContext):
	if not (await isUserReg(callback)): await callback.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	await callback.answer()
	data = await state.get_data()
	isGuestNow = 0
	if 'idUser' in data and 'id' in data:
		cur.execute('SELECT id FROM Queue WHERE idUser=? AND idMeeting=?;', (data['idUser'], data['id']))
		res = cur.fetchall()
		if res:
			isGuestNow = 'Да' if bool(res[0][0]) else 'Нет'
		else:
			await state.update_data(status='Не посетит событие')
	kbb = InlineKeyboardBuilder()
	txt = 'Для добавления информации нажать кнопки снизу.'
	if 'id' in data: txt += '\nID события: ' + str(data['id'])
	else: kbb.add(types.InlineKeyboardButton(text='ID события', callback_data="adminGuestId"))
	if 'idUser' in data: txt += '\nID пользователя: ' + str(data['idUser'])
	else: kbb.add(types.InlineKeyboardButton(text='ID пользователя', callback_data="adminGuestIdUser"))
	if isGuestNow:
		txt += '\Гость записан? ' + isGuestNow
	kbb.adjust(1, repeat=True)
	if 'id' and data and 'idUser' in data:
		kbb.add(types.InlineKeyboardButton(text='Подтвердить!', callback_data="adminGuestCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.newMeetingCheck)



@dp.callback_query(Text("adminGuestId"))
async def adminGuest(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('	SELECT Meeting.id, Meeting.name \
					FROM Queue \
					JOIN Meeting ON Queue.idMeeting = Meeting.id \
					WHERE ((Queue.idUser = ? AND Queue.isNewAdmin = TRUE) \
					OR Meeting.idCreator = ?) \
					AND Meeting.date > DATETIME(\'now\', \'localtime\');', (callback.from_user.id, callback.from_user.id))
	res = cur.fetchall()
	if not res: await callback.message.answer('На данный момент нет предстоящих событий, в которых Вы администратор.'); return 0
	kbb = InlineKeyboardBuilder()
	for item in res:
		kbb.add(types.InlineKeyboardButton(text='' + item[1], callback_data="adminGuestId " + str(item[0])))
	#await state.update_data(id=message.text)
	await callback.message.answer('Выберите событие:', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(SUPERText("adminGuestId "))
async def adminPayIdChoise(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('SELECT name FROM Meeting WHERE id=?;', (callback.data.split(' ')[1], ))
	await callback.message.answer('Выбрано событие ' + cur.fetchall()[0][0])
	await state.update_data(id=int(callback.data.split(' ')[1]))
	
	await adminPayCheck(callback, state)

@dp.callback_query(Text("adminGuestIdUser"))
async def adminPayIdUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID пользователя:')
	await state.set_state(Status.adminGuestIdUser)

@dp.message(Status.adminGuestIdUser)
async def adminPayIdUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="adminPayCheck"))
	await state.update_data(idUser=message.text)
	await message.answer('ID пользователя точно ' + str((await state.get_data())['idUser']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(Text("adminPayCreate"))
async def adminPayCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if not (await isUserReg(callback)): await callback.message.answer('Вас еще нет в системе. Зарегисироваться /reg'); await state.set_state(Status.nothing); return 0
	
	data = await state.get_data()
	idMeeting  = data['id']
	idUser  = data['idUser']

	cur.execute('DELETE FROM Queue WHERE idMeeting = ? AND idUser = ?;', (idMeeting, idUser))
	conn.commit()
	
	await callback.message.answer('Удаляю запись.')
	await state.set_state(Status.nothing)

# endregion
# region adminNew

@dp.callback_query(Text("adminNewCheck"))
async def adminNewCheck(callback: types.CallbackQuery, state: FSMContext):
	if not (await isUserReg(callback)): await callback.answer('Вы еще не в системе. Используйте /reg'); await state.set_state(Status.nothing); return 0
	await callback.answer()
	data = await state.get_data()
	if not ('status' in data) and 'idUser' in data and 'id' in data:
		cur.execute('SELECT isNewAdmin FROM Queue WHERE idUser=? AND idMeeting=?;', (data['idUser'], data['id']))
		res = cur.fetchall()
		if res:
			await state.update_data(status='Администратор' if bool(res[0][0]) else 'Не администратор')
			data = await state.get_data()
		else:
			await state.update_data(status='Не посетит событие')
	kbb = InlineKeyboardBuilder()
	txt = 'Для добавления информации нажать кнопки снизу.'
	if 'id' in data: txt += '\nID события: ' + str(data['id'])
	else: kbb.add(types.InlineKeyboardButton(text='ID события', callback_data="adminNewId"))
	if 'idUser' in data: txt += '\nID пользователя: ' + str(data['idUser'])
	else: kbb.add(types.InlineKeyboardButton(text='ID пользователя', callback_data="adminNewIdUser"))
	if 'status' in data: txt += '\nСтатус пользователя: ' + str(data['status'])
	kbb.add(types.InlineKeyboardButton(text='Статус пользователя', callback_data="adminNewIsNewAdmin"))
	kbb.adjust(1, repeat=True)
	if 'id' and data and 'idUser' in data:
		kbb.add(types.InlineKeyboardButton(text='Подтвердить!', callback_data="adminNewCreate"))
	await callback.message.answer(txt, reply_markup=kbb.as_markup(resize_keyboard=True))
	await state.set_state(Status.newMeetingCheck)



@dp.callback_query(Text("adminNewId"))
async def adminNewId(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('	SELECT Meeting.id, Meeting.name \
					FROM Queue \
					JOIN Meeting ON Queue.idMeeting = Meeting.id \
					WHERE Meeting.idCreator = ? \
					AND Meeting.date > DATETIME(\'now\', \'localtime\');', (callback.from_user.id, ))
	res = cur.fetchall()
	if not res: await callback.message.answer('На данный момент нет предстоящих событий, которые Вы создали.'); return 0
	kbb = InlineKeyboardBuilder()
	for item in res:
		kbb.add(types.InlineKeyboardButton(text='' + item[1], callback_data="adminNewId " + str(item[0])))
	#await state.update_data(id=message.text)
	await callback.message.answer('Выберите событие:', reply_markup=kbb.as_markup(resize_keyboard=True))

@dp.callback_query(SUPERText("adminNewId "))
async def adminNewIdChoise(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('SELECT name FROM Meeting WHERE id=?;', (callback.data.split(' ')[1], ))
	await callback.message.answer('Выбрано событие ' + cur.fetchall()[0][0])
	await state.update_data(id=int(callback.data.split(' ')[1]))
	
	await adminNewCheck(callback, state)

@dp.callback_query(Text("adminNewIdUser"))
async def adminNewIdUser(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await callback.message.answer('Введите ID пользователя:')
	await state.set_state(Status.adminNewIdUser)

@dp.message(Status.adminNewIdUser)
async def adminNewIdUserWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="adminNewCheck"))
	await state.update_data(idUser=message.text)
	await message.answer('ID пользователя точно ' + str((await state.get_data())['idUser']) + '? Если нет, введите еще раз.', reply_markup=kbb.as_markup(resize_keyboard=True))



@dp.callback_query(Text("adminNewIsNewAdmin"))
async def adminNewIsNewAdmin(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Администратор', callback_data="adminNewIsNewAdminTrue"))
	kbb.add(types.InlineKeyboardButton(text='Не администратор', callback_data="adminNewIsNewAdminFalse"))
	await callback.message.answer('Выберите статус пользователя:', reply_markup=kbb.as_markup(resize_keyboard=True))
@dp.callback_query(Text("adminNewIsNewAdminTrue"))
async def adminNewIsNewAdminTrue(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await state.update_data(status='Администратор')
	await adminNewCheck(callback, state)
@dp.callback_query(Text("adminNewIsNewAdminFalse"))
async def adminNewIsNewAdminFalse(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	await state.update_data(status='Не администратор')
	await adminNewCheck(callback, state)



@dp.callback_query(Text("adminNewCreate"))
async def aadminNewCreate(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	if not (await isUserReg(callback)): await callback.message.answer('Вас еще нет в системе. Зарегисироваться /reg'); await state.set_state(Status.nothing); return 0
	
	data = await state.get_data()
	idMeeting  = data['id']
	idUser  = data['idUser']
	isNewAdmin = True if data['status'] == 'Администратор' else False

	cur.execute('UPDATE `Queue` SET `isNewAdmin`=? WHERE `idMeeting`=? AND idUser=?;', (isNewAdmin, idMeeting, idUser))
	conn.commit()
	
	await callback.message.answer('Добавляю запись.')
	await state.set_state(Status.nothing)

# endregion
# region adminUser

@dp.callback_query(Text("adminUserCheck"))
async def adminUserCheck(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	
	await callback.message.answer('Введите ник, тег, имя и фамилию через пробел или id пользрователя для получения всей возможной информации о нем.')
	await state.set_state(Status.adminUserCheck)

@dp.message(Status.adminUserCheck)
async def adminUserCheckWait(message: types.Message, state: FSMContext):
	kbb = InlineKeyboardBuilder()
	kbb.add(types.InlineKeyboardButton(text='Да, дальше', callback_data="adminNewCheck"))

	cur.execute('SELECT * FROM User WHERE id=? OR (name1 = ? AND name2 = ?) OR telega_name=? OR telega_tag=?', (message.text, (str(message.text) + '  ').split(' ')[0], (str(message.text) + '  ').split(' ')[1], message.text, message.text))
	ret = cur.fetchall()
	if ret:
		ret = ret[0]
		txt = 	'ID     =' + str(ret[0]) + '\n' + \
				'Имя    =' + str(ret[1]) + '\n' + \
				'Фамилия=' + str(ret[2]) + '\n' + \
				'Ник    =' + str(ret[4]) + '\n' + \
				'Тег    =' + str(ret[5])
	else:
		txt = 'Пользователя еще нет в системе или в запросе ошибка.'

	await message.answer(txt)

# endregion
# region adminList



# endregion

@dp.callback_query(Text("adminList"))
async def adminList(callback: types.CallbackQuery, state: FSMContext):
	await callback.answer()
	cur.execute('	SELECT Meeting.id, Meeting.name, Meeting.notificationText \
					FROM Queue \
					JOIN Meeting ON Queue.idMeeting = Meeting.id \
					WHERE ((Queue.idUser = ? AND Queue.isNewAdmin = TRUE) \
					OR Meeting.idCreator = ?) \
					AND Meeting.date > DATETIME(\'now\', \'localtime\');', (callback.from_user.id, callback.from_user.id))
	res = cur.fetchall()
	if not res: await callback.message.answer('На данный момент нет предстоящих событий, в которых Вы администратор.'); return 0
	txt = 'События:'
	for item in res:
		txt += '\n ' + str(item[0]) + ' - "' + str(item[1]) + '": ' + str(item[2]) + '.'

	await callback.message.answer(txt)
# endregion

@dp.message(Command('ping'))
async def send_welcome(message: types.Message, state: FSMContext, dialog_manager: DialogManager = DialogManager):
	if message.text == '/ping all':
		await message.answer(str(message))
	elif message.text == '/ping id':
		await message.answer(str(message.chat.id))
	elif message.text == '/ping' or message.text == '/ping help':
		await message.answer('Простой способ получить отладочную информацию.\nusage: /ping [all|id|help|num]\n/ping all - all data\n/ping id - chat id\n/ping help - this message\n/ping num - id of /ping answer')
	elif message.text == '/ping num':
		await message.answer(str(message.message_id))


	


async def on_startup_and_daily():
	aioschedule.clear()
	
	aioschedule.every().day.at('00:00').do(on_startup_and_daily)
	while True:
		#print(da)
		await aioschedule.run_pending()
		await asyncio.sleep(1)

async def main():
	await notification_assigner()
	#await notification_dealer(2041547209, 'asdasd')
	
	await dp.start_polling(bot)
	print('asd')
	#await bot.send_message(2041547209, 'asdasd')
	#daad = SendMessage(2041547209, 'asdasd')


if __name__ == "__main__":
	
	loop = asyncio.new_event_loop()
	tsk1 = loop.create_task(on_startup_and_daily())
	tsk2 = loop.create_task(main())
	tsk1.add_done_callback(lambda t: print(f'Task done: {t.result()} << return val of first task'))
	tsk2.add_done_callback(lambda t: print(f'Task done: {t.result()} << return val of second task'))
	
	loop.run_forever()

	#asyncio.run(main())
	