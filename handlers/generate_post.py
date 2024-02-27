from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, InputMediaPhoto, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from main_func import InstagramPublish, openAIapi, GoogleSearch
from keyboards.default import defaultState
from aiogram.methods import send_media_group
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio



instagram = InstagramPublish()
openAI = openAIapi()
googleSearch = GoogleSearch()

allowed_users = [1010283485, 668442122, 1]

class Authentication(StatesGroup):
    authorised = State()

class CommonStates(StatesGroup):
    themeChoosing = State()
    postGenerating = State()
    imageChoosing = State()

    tokenChanging = State()


class MainRouter:
    def __init__(self) -> None:
        self.photoUrls = []
        self.photos=[]

    async def cmd_start(self, message: Message, state: FSMContext):
        await state.clear()
        if message.from_user.id in allowed_users or 1 in allowed_users:
            await message.answer(text="Вы были авторизированы! Добро пожаловать", reply_markup=defaultState())
            await state.set_state(Authentication.authorised)
        else:
            await message.answer(text="Вы не находитесь в списке пользователей.") 

    async def cmd_cancel(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            text="Действие отменено",
            reply_markup=ReplyKeyboardRemove()
        )

    async def choose_theme(self, message: Message, state: FSMContext):
        await message.answer("Напишите тему поста:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CommonStates.postGenerating)

    async def create_post(self, message: Message, state: FSMContext):
        await message.answer("Cоздание поста..")
        self.answer, self.photoUrls = await asyncio.gather(
        openAI.makeCompletion(message.text),
        googleSearch.google_web_search(message.text)
    )
        print(self.photoUrls)
        if len(self.photoUrls)>1:
            media = [InputMediaPhoto(media=url) for url in self.photoUrls]
            print(media)
            builder = ReplyKeyboardBuilder()
            # self.photos = []
            for i in range(1, len(self.photoUrls)+1):
                # self.photos.append(i)
                builder.add(KeyboardButton(text=str(i)))
            builder.adjust(5)
            await message.answer_media_group(media=media)
            await message.answer(self.answer, reply_markup=builder.as_markup(resize_keyboard=True))
            await state.set_state(CommonStates.imageChoosing)
        else:
            await message.answer("Ууупс! Кажется, фотографии по теме не были найдены. Введите другое ключевое слово :c")
            await state.set_state(CommonStates.postGenerating)

    async def image_choose(self, message: Message, state: FSMContext):
        try:
            num = int(message.text)
            print(num)
            print(self.photoUrls)
            if num < 0 or num > len(self.photoUrls):
                await message.answer("Изображения под таким номером не существует!")
                await state.set_state(CommonStates.imageChoosing)
            else:
                self.photo = self.photoUrls[num-1]
                print(self.photo)
                kb = [
                    [InlineKeyboardButton(text="Опубликовать в инстаграм", callback_data="instagram_publish")]
                ]
                keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
                await message.answer_photo(photo=self.photo, caption="Выбранное изображение будет опубликовано!", reply_markup=keyboard)
                await state.set_state(Authentication.authorised)
        except:
            await message.answer("Изображения под таким номером не существует!")
            await state.set_state(CommonStates.imageChoosing)
    
    async def instagram_send(self, callback):
        await callback.message.answer("Публикация...", reply_markup = defaultState())
        creationId = await instagram.upload_photo(self.photo, self.answer)
        print(creationId)
        await instagram.instagram_publish(creationId)
        kb = [
                    [InlineKeyboardButton(text="@deikaiblog", url="https://www.instagram.com/deikaiblog/")]
                ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.answer("Пост был опубликован в инстаграм!", reply_markup=keyboard)

    async def token_choosing(self, message: Message, state: FSMContext):
        await message.reply("Укажите новый токен: ", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CommonStates.tokenChanging)

    async def token_changing(self, message: Message, state: FSMContext):
        result = instagram.graph_token_change(message.text)
        await message.reply(result, reply_markup=defaultState())
        await state.set_state(Authentication.authorised)
    


main_router = MainRouter()

router = Router()
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await main_router.cmd_start(message, state)

@router.message(Command("cancel"))
@router.message(F.text.lower() == "отмена")
async def cancel(message: Message, state: FSMContext):
    await main_router.cmd_cancel(message, state)

@router.message(Command("token_change"), Authentication.authorised)
async def tokenChoosing(message: Message, state: FSMContext):
    await main_router.token_choosing(message, state)

@router.message(F.text, CommonStates.tokenChanging)
async def tokenChanging(message: Message, state: FSMContext):
    await main_router.token_changing(message, state)

@router.message(Command("createPost"), Authentication.authorised)
async def chooseTheme(message: Message, state: FSMContext):
    await main_router.choose_theme(message, state)

@router.message(F.text, CommonStates.postGenerating)
async def createPost(message: Message, state: FSMContext):
    await main_router.create_post(message, state)

@router.message(CommonStates.imageChoosing, F.text)
async def imageChoose(message: Message, state: FSMContext):
    await main_router.image_choose(message, state)

@router.callback_query(F.data=="instagram_publish")
async def instagramSend(callback = CallbackQuery):
    await main_router.instagram_send(callback)
