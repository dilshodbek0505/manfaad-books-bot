from aiogram import Router, types, F , Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from apps.bot.keyboards.reply import reply_main_menu, reply_contact
from apps.bot.keyboards.inline import inline_languages, inline_searches
from apps.bot.utils.states import RegisterStatesGroup, SearchStatesGruop
from apps.bot.utils.callback_data import SelectLanguageCallbackData, SelectSearchCallbackData

from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.books.models import Books,Books_population
from django.db import models
from django.db.models import Count

from aiogram.types import FSInputFile,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton

import re
from apps.bot.handlers.settings import Books_search

from asgiref.sync import sync_to_async
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.bot.config.config import BOT_TOKEN

router = Router()
User = get_user_model()

bot = Bot(token=BOT_TOKEN)


ITEMS_PER_PAGE = 5

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    try:
        user = await User.objects.aget(id = message.from_user.id)    
        await state.clear()
        await message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())

    except Exception as err:
        await message.answer(_("Keling siz bilan yaqindan tanishib olamiz 😊"))
        await message.answer(_("Ismingiz: "))
        await state.set_state(RegisterStatesGroup.full_name)


@router.message(F.text, RegisterStatesGroup.full_name)
async def register_full_name(messages: types.Message, state: FSMContext):
    await state.update_data({
        "full_name": messages.text
    })

    await messages.answer(_("Telfon raqamingizni yuboring:"), reply_markup=reply_contact())
    await state.set_state(RegisterStatesGroup.phone)

@router.message(F.text, RegisterStatesGroup.phone)
async def register_phone_text(messages: types.Message, state: FSMContext):
    await state.update_data({
        "phone": messages.text
    })
    
    await messages.answer(_("Tilni tanlang: "), reply_markup=inline_languages())
    await state.set_state(RegisterStatesGroup.language)

@router.message(F.contact, RegisterStatesGroup.phone)
async def register_phone_contact(messages: types.Message, state: FSMContext):
    await state.update_data({
        "contact": messages.contact.phone_number
    })

    await messages.answer(_("Tilni tanlang: "), reply_markup=inline_languages())
    await state.set_state(RegisterStatesGroup.language)

@router.callback_query(RegisterStatesGroup.language, SelectLanguageCallbackData.filter())
async def register_langauge(callback_query: types.CallbackQuery, callback_data: SelectLanguageCallbackData, state: FSMContext):
    from apps.bot.management.commands.runbot import i18n

    cache_key = f"user_language_{callback_query.from_user.id}"
    await cache.aset(cache_key, callback_data.language.value)
    
    i18n.ctx_locale.set(callback_data.language.value)

    data = await state.get_data()
    
    try:
        await User.objects.acreate(
            id = callback_query.from_user.id,
            phone = data.get('phone'),
            first_name = data.get('full_name'),
            language = callback_data.language.value
        )
    except Exception as err:
        await callback_query.message.answer(_("Xatolik yuz berdi 😢"))
        
    await callback_query.message.answer(_("Botga xush kelibsiz!"), reply_markup=reply_main_menu())

    await state.clear()

    await callback_query.answer(cache_time=0)

@router.callback_query(SelectSearchCallbackData.filter(), SearchStatesGruop.books )
@router.callback_query(lambda c: c.data.startswith("all_books_"))
async def searching(callback_query: types.CallbackQuery, state: FSMContext,callback_data: SelectSearchCallbackData=None  ):
    call_data=False
    if callback_data:
        if callback_data.searching.value == "name":

            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            data = await state.get_data()
            if "book_message_id" in data:
                await bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=data["book_message_id"]
                )

            reply_message=await callback_query.message.answer(_("Kitob nomini yozib yuboring:"))

            await state.update_data(name_callback=reply_message.message_id)

            await state.set_state(SearchStatesGruop.search_name)





            # await message.answer(_("<b>Sizning sharhingiz\n\n</b>{comment}\n").format(comment = comment_text), reply_markup=inline_confirm())

        
        elif callback_data.searching.value == "author":
            
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            data = await state.get_data()
            if "book_message_id" in data:
                await bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=data["book_message_id"]
                )

            reply_message=await callback_query.message.answer(_("Kitob muallifini yozib yuboring:"))

            await state.update_data(author_callback=reply_message.message_id)

            await state.set_state(SearchStatesGruop.search_author)

        elif callback_data.searching.value == "all":
            call_data=True

    if call_data or callback_query.data:
        # Page ma'lumotlarini olish
        data_parts = callback_query.data.split('_')
        page = int(data_parts[-1]) if len(data_parts) > 2 else 1    

        # Bazadan kitoblarni olish
        books_usage = await sync_to_async(list)(
            Books_population.objects.values('book_id')
            .annotate(usage_count=Count('book_id'))  # book_id ni necha marta ishlatganini hisoblash
            .order_by('-usage_count')  # usage_count bo'yicha kamayish tartibida saralash
        )


        sorted_book_ids = [entry['book_id'] for entry in books_usage]


        used_books = await sync_to_async(list)(
        Books.objects.filter(id__in=sorted_book_ids)
        .order_by(models.Case(*[models.When(id=id, then=models.Value(i)) for i, id in enumerate(sorted_book_ids)]))
    )


        remaining_books = await sync_to_async(list)(
            Books.objects.exclude(id__in=sorted_book_ids)
        )
        all_books = used_books + remaining_books

        total_books = len(all_books)

        if total_books == 0:
            await callback_query.message.reply(_("❌ Kitoblar topilmadi."))
            return

        # Sahifa bo'yicha kitoblarni ajratish
        start_index = (page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        books_on_page = all_books[start_index:end_index]

        # Inline keyboard yaratish
        keyboard_builder = InlineKeyboardBuilder()

        for i in range(0, len(books_on_page), 2):
            books_row = books_on_page[i:i + 2]
            keyboard_builder.row(
                *[
                    InlineKeyboardButton(
                        text=f"{book.name}",
                        callback_data=f"book_{book.id}"
                    )
                    for book in books_row
                ]
            )

        # Navigatsiya tugmalari
        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text=_("⬅ Oldingi"),
                    callback_data=f"all_books_{page - 1}"
                )
            )
        if end_index < total_books:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text=_("Keyingi ➡"),
                    callback_data=f"all_books_{page + 1}"
                )
            )

        if navigation_buttons:
            keyboard_builder.row(*navigation_buttons)

        # Foydalanuvchiga xabar yuborish
        try:
            reply_markup = keyboard_builder.as_markup()
            await callback_query.message.edit_text(
                _("🔍 Barcha kitoblar eng mashhurlik bo‘yicha saralangan:"),
                reply_markup=reply_markup,
            )
            data = await state.get_data()
            if "book_message_id" in data:
                await bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=data["book_message_id"])
        except TelegramBadRequest:
            pass
        # State saqlash (keyingi holatlar uchun)
        await state.update_data(search_message_id=callback_query.message.message_id)
        


    await callback_query.answer()
    


@router.message(F.text, SearchStatesGruop.search_name)
@router.callback_query(F.data.startswith("research_name_"))
async def searching_name(message_or_query: types.Message | types.CallbackQuery, state: FSMContext,):
    
    if isinstance(message_or_query, types.Message):
        query = message_or_query.text.strip()
        data = await state.get_data()
        if "name_callback" in data:
            await bot.delete_message(
                chat_id=message_or_query.chat.id,
                message_id=data["name_callback"]
            )
        page = 1
    elif isinstance(message_or_query, types.CallbackQuery):
        query = message_or_query.data.split('_')[2]
        # await bot.delete_message(chat_id=message_or_query.message.chat.id, message_id=message_or_query.message.message_id)
        data_parts = message_or_query.data.split('_')
        page = int(data_parts[-1]) if len(data_parts) > 3 else 1
        

    
    await state.clear()
    try:
        # Kitobni qidirish
        all_books = await sync_to_async(list)(Books.objects.all().filter(name__icontains=query))

        total_books = len(all_books)

        if total_books > 0:
            
            start_index = (page - 1) * ITEMS_PER_PAGE
            end_index = start_index + ITEMS_PER_PAGE
            books = all_books[start_index:end_index]
            if all_books:
                keyboard_builder = InlineKeyboardBuilder()
                for i in range(0, len(books), 2):
                    books_row = books[i:i + 2]
                    keyboard_builder.row(
                        *[
                            InlineKeyboardButton(
                                text=book.name,
                                callback_data=f"book_{book.pk}_{query}"
                            )
                            for book in books_row
                        ]
                    )
                    
                navigation_buttons = []

                if page > 1:
                    navigation_buttons.append(
                        InlineKeyboardButton(
                            text=_("⬅ Oldingi"),
                            callback_data=f"research_name__{query}_{page - 1}"
                        )
                    )

                if end_index < total_books:
                    navigation_buttons.append(
                        InlineKeyboardButton(
                            text=_("Keyingi ➡"),
                            callback_data=f"research_name__{query}_{page + 1}"
                        )
                    )


            
            if navigation_buttons:
                keyboard_builder.row(*navigation_buttons)  # Alohida qator
            
            reply_markup = keyboard_builder.as_markup()
            if isinstance(message_or_query, types.Message):
                reply_massage=await message_or_query.answer(
                    _("🔍 Siz qidirgan kitoblardan birini tanlang:"),
                    reply_markup=reply_markup
                )
                await state.update_data(search_message_id=reply_massage.message_id)
                await state.update_data(search_message_name=message_or_query.message_id)
            elif isinstance(message_or_query, types.CallbackQuery):
                try:
                    reply_massage= await message_or_query.message.edit_text(
                        _("🔍 Siz qidirgan kitoblardan birini tanlang:"),
                        reply_markup=reply_markup
                    )
                    
                except TelegramBadRequest:
                    await bot.delete_message(chat_id=message_or_query.message.chat.id, message_id=message_or_query.message.message_id)
                    reply_massage= await message_or_query.message.answer(
                        _("🔍 Siz qidirgan kitoblardan birini tanlang:"),
                        reply_markup=reply_markup
                    )
                await state.update_data(search_message_id=reply_massage.message_id)
        else:
            if isinstance(message_or_query, types.Message):
                reply_massage=await message_or_query.reply(_("❌ Bunday kitob topilmadi. Iltimos, boshqa nom kiriting.") ,reply_markup=reply_main_menu())
                await state.update_data(search_message_id=reply_massage.message_id)
                await state.update_data(search_message_name=message_or_query.message_id)

    except Exception as e:
        if isinstance(message_or_query, types.CallbackQuery):
            await message_or_query.answer(_(f"⚠️ Xatolik yuz berdi. Keyinroq urinib ko'ring.")) 
         


@router.message(F.text, SearchStatesGruop.search_author)
@router.callback_query(F.data.startswith("research_author_"))
async def search_authors_by_name_prefix( message_or_query: types.Message | types.CallbackQuery, state: FSMContext):
    
    if isinstance(message_or_query, types.Message):
        data = await state.get_data()
        if "author_callback" in data:
            await bot.delete_message(
                chat_id=message_or_query.chat.id,
                message_id=data["author_callback"]
            )
        query = message_or_query.text.strip()
        page = 1


    elif isinstance(message_or_query, types.CallbackQuery):
        # await bot.delete_message(chat_id=message_or_query.message.chat.id, message_id=message_or_query.message.message_id)
        query=message_or_query.data.split('_')[3]
        data_parts = message_or_query.data.split('_')
        page = int(data_parts[4]) if len(data_parts) > 4 else 1


    await state.clear()
    books = await sync_to_async(list)(Books.objects.all().filter(author_name__istartswith=query))  # Muallifni qidirish
    total_books = len(books)
    if books:
        if total_books > 0:
            start_index = (page - 1) * ITEMS_PER_PAGE
            end_index = start_index + ITEMS_PER_PAGE
            authors = books[start_index:end_index]
            
            # Inline keyboard uchun tugmalar
            unique_authors = [book.author_name for book in authors]
            unique_authors.sort()

            keyboard_builder = InlineKeyboardBuilder()
            for i in range(0, len(unique_authors), 2):
                # Har bir qator uchun ikki muallif nomini olish
                authors_row = unique_authors[i:i + 2]

                # Tugmalarni qo'shish
                keyboard_builder.row(
                    *[
                        InlineKeyboardButton(
                            text=author_name,
                            callback_data=f"author_{author_name}_{query}"
                        )
                        for author_name in authors_row
                    ]
                    )

            navigation_buttons = []

            if page > 1:
                navigation_buttons.append(
                    InlineKeyboardButton(
                        text=_("⬅ Oldingi"),
                        callback_data=f"research_author__{query}_{page - 1}"
                    )
                )

            if end_index < total_books:
                navigation_buttons.append(
                    InlineKeyboardButton(
                        text=_("Keyingi ➡"),
                        callback_data=f"research_author__{query}_{page + 1}"
                    )
                )


            
            if navigation_buttons:
                keyboard_builder.row(*navigation_buttons)  # Alohida qator

            reply_markup = keyboard_builder.as_markup()
            if isinstance(message_or_query, types.Message):
                reply_massage=await message_or_query.reply(
                    _("🔍 {query} so'zidan boshlangan mualliflar topildi:").format(query = query),
                    reply_markup=reply_markup,
                )
            elif isinstance(message_or_query, types.CallbackQuery):
                try:
                    reply_massage=await message_or_query.message.edit_text(
                        _("🔍 {query} so'zidan boshlangan mualliflar topildi:").format(query = query),
                        reply_markup=reply_markup,
                    )
                except TelegramBadRequest: 
                    pass
    else:
        if isinstance(message_or_query, types.Message):
            await message_or_query.reply(
                _("❌ {query} bilan boshlangan muallif topilmadi. Qayta urinib ko'ring").format(query = query), reply_markup=reply_main_menu()
            )

    await state.clear()
    if isinstance(message_or_query, types.Message):
        await state.update_data(search_message_id=reply_massage.message_id)
        await state.update_data(search_message_name=message_or_query.message_id)
    elif isinstance(message_or_query, types.CallbackQuery):
        await state.update_data(search_message_id=message_or_query.message.message_id)

@router.callback_query(F.data.startswith("author_"))
async def send_author_by_callback(callback_query: types.CallbackQuery,state: FSMContext):
    # await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    data_parts = callback_query.data.split('_')
    author = data_parts[1]
   
    query = data_parts[2]
    page = int(data_parts[3]) if len(data_parts) > 3 else 1


    try:
        # Kitobni olish
        all_books = await sync_to_async(list)(Books.objects.all().filter(author_name=author))

        total_books = len(all_books)


        if all_books:
            if total_books > 0:

                start_index = (page - 1) * ITEMS_PER_PAGE
                end_index = start_index + ITEMS_PER_PAGE
                books = all_books[start_index:end_index]

                keyboard_builder = InlineKeyboardBuilder()


                for i in range(0, len(books), 2):
                    buttons_row = books[i:i + 2]


                    keyboard_builder.row(
                            *[
                                InlineKeyboardButton(
                                    text=book.name,
                                    callback_data=f"book_{book.pk}_l_{query}"
                                )
                                for book in buttons_row
                            ]
                        )
                navigation_buttons = []

                navigation_buttons.append(
                        InlineKeyboardButton(
                        text=_("Orqaga"),
                        callback_data=f"research_author_L_{query}"
                    )
                )

                
                if page > 1:

                    navigation_buttons.append(
                        InlineKeyboardButton(
                            text=_("⬅ Oldingi"),
                            callback_data=f"author_{author}_{query}_{page - 1}"
                        )
                    )

                if end_index < total_books:
                    navigation_buttons.append(
                        InlineKeyboardButton(
                            text=_("Keyingi ➡"),
                            callback_data=f"author_{author}_{query}_{page + 1}"
                        )
                    )

                
                if navigation_buttons:
                    keyboard_builder.row(*navigation_buttons)

                    
                reply_markup = keyboard_builder.as_markup()
                try:
                    reply_message=await callback_query.message.edit_text(_("{author} yozgan barcha kitoblar:").format(author = author),reply_markup=reply_markup)
                except TelegramBadRequest:
                    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
                    reply_message=await callback_query.message.answer(_("{author} yozgan barcha kitoblar:").format(author = author),reply_markup=reply_markup)
    except Books.DoesNotExist:
        reply_message=await callback_query.message.answer(_("❌ Bu muallif hali kitob yozmagan."),reply_markup=reply_markup)
    except    Exception as e:
        await callback_query.message.answer(_("⚠️ Xatolik yuz berdi"))

    await callback_query.answer()
    # await state.update_data(search_message_id=reply_message.message_id)



@router.callback_query(F.data.startswith("book_"))
async def send_book_by_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    try:
        book_id = int(re.split(r"[_-]", callback_query.data)[1])
        query = callback_query.data.split('_')[3]
        
    except IndexError:
        book_id = int(re.split(r"[_-]", callback_query.data)[1])
        query=None
        query_name = re.split(r"[_-]", callback_query.data)[-1]
    try:
        # Kitobni olish
        book = await sync_to_async(list)(Books.objects.all().filter(pk=book_id))
        related_entry= await sync_to_async(list)(Books_population.objects.select_related("book").filter(telegram_id=callback_query.from_user.id, book_id=book_id))
        print(related_entry)
        if not related_entry:
             related_entry = await sync_to_async(Books_population.objects.create)(
                telegram_id=callback_query.from_user.id,
                book_id=book_id,  # `book_id` orqali bog'lash
            )
           
        
        for books in book:
            
            pdf_file = FSInputFile(books.book.path)
            keyboard_builder = InlineKeyboardBuilder()
            keyboard_builder.button(text=_("Audio Faylni Yuklash📥"), callback_data=f"audio_{book_id}")
            if query :
                keyboard_builder.button(text=_("Orqaga"), callback_data=f"author_{books.author_name}_{query}")
            elif query_name.isdigit() :
                pass
            elif not query_name.isdigit():
                keyboard_builder.button(text=_("Orqaga"), callback_data=f"research_name_{query_name}")
            reply_markup = keyboard_builder.as_markup()
            # Audio yuborish
            await callback_query.message.answer_document(
                pdf_file, caption=_(
                    "📖 Kitob: {books_name}\n✍️ Muallif: {author_name}\n  {desc}"
                    ).format(

                        books_name= books.name,
                        author_name = books.author_name,
                        desc=books.desc 

                        ),reply_markup=reply_markup
            )
    except Books.DoesNotExist:
        await callback_query.message.answer(_("❌ Bu kitob topilmadi."))
    except Exception as e:
        await state.clear()
        await callback_query.message.answer(_("⚠️ Xatolik yuz berdi"))
    await state.clear()
    await callback_query.answer()
    
    
    



@router.callback_query(F.data.startswith("audio_"))
async def send_audio_by_callback(callback_query: types.CallbackQuery):
    book_id = int(callback_query.data.split('_')[1])
    try:
        book = await sync_to_async(list)(Books.objects.all().filter(pk=book_id))
        
        for books in book:
            audio_path = books.audio.path
            audio_file = FSInputFile(audio_path)
            # Audio yuborish
            await callback_query.message.answer_audio(
                audio_file,title=f"{books.name}-{books.author_name}"
            )
    except Books.DoesNotExist:
        await callback_query.message.answer(_("❌ Bu kitob topilmadi."))
    except Exception as e:
        await callback_query.message.answer(_("⚠️ Xatolik yuz berdi"))

    await callback_query.answer()
    