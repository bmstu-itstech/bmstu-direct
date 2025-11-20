import logging
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, IsReplyFilter
from aiogram.types import (
    ChatType,
    ContentType,
    InputMediaDocument,
    InputMediaPhoto,
    Message,
    ParseMode,
    ReplyKeyboardRemove,
)

from core import texts
from core import states
from core import domain
from core.domain import TicketRecord, Status
from core.handlers import keyboards
from common.repository import dp, bot
from common.swear_words import escape_swear_words
from services.db.storage import MessageNotFoundException, Storage
from core.filters.role import StudentFilter

from config import config


# Ключи для сохранения промежуточных данных в словаре
# контексте конечного автомата.
DATA_ISSUE_KEY = "issue"
DATA_CATEGORY_KEY = "category"
DATA_ANONYM_KEY = "is_anonym"
DATA_FULL_NAME_KEY = "full_name"
DATA_STUDY_GROUP_KEY = "study_group"
DATA_TEXT_KEY = "text"


logger = logging.getLogger(__name__)


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state="*", commands=["start"])
async def send_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(
        texts.ticket.greet,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    await send_create_ticket(message)


async def send_create_ticket(message: Message):
    await message.answer(
        texts.ticket.create_ticket,
        reply_markup=keyboards.create_ticket_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.create_ticket.set()


@dp.message_handler(
    StudentFilter(),
    IsReplyFilter(is_reply=False),
    content_types=[
        ContentType.AUDIO,
        ContentType.DOCUMENT,
        ContentType.PHOTO,
        ContentType.STICKER,
        ContentType.VIDEO,
        ContentType.VOICE,
        ContentType.LOCATION,
        ContentType.CONTACT,
        ContentType.POLL,
        ContentType.DICE,
        ContentType.VIDEO_NOTE,
        ContentType.ANIMATION,  # GIF
    ],
    state="*",
)
async def handle_no_text(message: Message):
    await message.answer(
        texts.errors.message_no_text,
        parse_mode=ParseMode.HTML
    )


@dp.message_handler(
    ChatTypeFilter(ChatType.PRIVATE),
    IsReplyFilter(is_reply=True),
    state="*",
    content_types=[ContentType.ANY],
)
async def handle_student_answer(message: Message, store: Storage, album: list[Message] | None = None):
    ticket_ids = await store.chat_ticket_ids(message.chat.id)
    try:
        replied_message = await store.message_by_id(
            ticket_ids=ticket_ids,
            owner_message_id=message.reply_to_message.message_id,
        )
    except MessageNotFoundException:
        await message.answer(texts.errors.no_reply, parse_mode=ParseMode.HTML)
        return
    answer = escape_swear_words(
        message.html_caption or message.html_text or message.caption or message.text or ""
    )
    await send_student_answer(message, store, replied_message, answer, album)


async def send_student_answer(
    message: Message,
    store: Storage,
    replied_message: domain.Message,
    answer: str,
    album: list[Message] | None,
):
    reply_to_id = replied_message.message_id
    sent: list[Message]
    album_messages: list[Message] | None = None
    # Если документ
    if message.content_type == ContentType.DOCUMENT:
        if message.media_group_id is None:
            file_id = message.document.file_id
            sent = [
                await bot.send_document(
                    config.comment_chat_id,
                    document=file_id,
                    reply_to_message_id=reply_to_id,
                    parse_mode=ParseMode.HTML,
                    caption=texts.ticket.student_answer(answer),
                )
            ]
        else:
            media = []
            album_messages = album or [message]
            for idx, obj in enumerate(album_messages):
                media.append(
                    InputMediaDocument(
                        media=obj.document.file_id,
                        caption=texts.ticket.student_answer(answer) if idx == 0 else None,
                        parse_mode=ParseMode.HTML if idx == 0 else None,
                    )
                )
            sent = await bot.send_media_group(
                chat_id=config.comment_chat_id, media=media, reply_to_message_id=reply_to_id
            )
    # Если фото
    elif message.content_type == ContentType.PHOTO:
        if message.media_group_id is None:
            file_id = message.photo[-1].file_id
            sent = [
                await bot.send_photo(
                    config.comment_chat_id,
                    photo=file_id,
                    reply_to_message_id=reply_to_id,
                    parse_mode=ParseMode.HTML,
                    caption=texts.ticket.student_answer(answer),
                )
            ]
        else:
            media = []
            album_messages = album or [message]
            for idx, obj in enumerate(album_messages):
                media.append(
                    InputMediaPhoto(
                        media=obj.photo[-1].file_id,
                        caption=texts.ticket.student_answer(answer) if idx == 0 else None,
                        parse_mode=ParseMode.HTML if idx == 0 else None,
                    )
                )
            sent = await bot.send_media_group(
                chat_id=config.comment_chat_id, media=media, reply_to_message_id=reply_to_id
            )
    # Текстовые сообщения
    elif message.content_type == ContentType.TEXT:
        sent = [
            await bot.send_message(
                config.comment_chat_id,
                texts.ticket.student_answer(answer),
                reply_to_message_id=reply_to_id,
                parse_mode=ParseMode.HTML,
            )
        ]
    # Любые другие типы (видео, аудио и пр.)
    else:
        target_album = album or [message]
        sent = []
        for idx, obj in enumerate(target_album):
            caption = texts.ticket.student_answer(answer) if idx == 0 else None
            sent.append(
                await obj.copy_to(
                    config.comment_chat_id,
                    reply_to_message_id=reply_to_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML if caption else None,
                )
            )

    if message.media_group_id and len(sent) > 1:
        album_messages = album_messages or album or [message]
        for reply_msg, owner_msg in zip(sent, album_messages):
            await store.save_message(
                domain.Message(
                    chat_id=reply_msg.chat.id,
                    message_id=reply_msg.message_id,
                    owner_message_id=owner_msg.message_id,
                    reply_to_message_id=reply_msg.reply_to_message.message_id if reply_msg.reply_to_message else reply_to_id,
                    ticket_id=replied_message.ticket_id,
                )
            )
    else:
        await store.save_message(
            domain.Message(
                chat_id=sent[0].chat.id,
                message_id=sent[0].message_id,
                owner_message_id=message.message_id,
                reply_to_message_id=sent[0].reply_to_message.message_id if sent[0].reply_to_message else reply_to_id,
                ticket_id=replied_message.ticket_id,
            )
        )


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.create_ticket, regexp=texts.buttons.create_ticket)
async def handle_create_ticket(message: Message):
    await send_choice_issue(message)


async def send_choice_issue(message: Message):
    await message.answer(
        texts.ticket.choice_issue,
        reply_markup=keyboards.choice_issue_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.choice_issue.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.choice_issue)
async def handle_choice_issue(message: Message, state: FSMContext):
    if message.text == texts.buttons.back:
        return await send_cancel_ticket(message)
    issue = map_button_to_issue(message.text)
    if not issue:
        return await send_choice_issue_invalid(message)
    async with state.proxy() as data:
        data[DATA_ISSUE_KEY] = issue
    await send_choice_category(message)


async def send_cancel_ticket(message: Message):
    await message.answer(texts.ticket.cancel_ticket, reply_markup=keyboards.create_ticket_keyboard())
    await states.Registration.create_ticket.set()


async def send_choice_issue_invalid(message: Message):
    await message.answer(
       texts.errors.invalid_input_button,
    )
    await send_choice_issue(message)


async def send_choice_category(message: Message):
    await message.reply(
        texts.ticket.choice_category,
        reply_markup=keyboards.choice_category_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.choice_category.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.choice_category)
async def handle_choice_category(message: Message, state: FSMContext):
    if message.text == texts.buttons.back:
        return await send_choice_issue(message)
    category = map_button_to_category(message.text)
    if not category:
        return await send_choice_category_invalid(message)
    if category is domain.Category.MILITARY:
        return await send_choice_category_military(message)
    if category is domain.Category.ADMISSION:
        return await send_choice_category_admission(message)
    async with state.proxy() as data:
        data[DATA_CATEGORY_KEY] = category
    await send_choice_privacy(message)


async def send_choice_category_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_button)
    await send_choice_category(message)


async def send_choice_category_military(message: Message):
    await message.answer(texts.ticket.chosen_military, reply_markup=ReplyKeyboardRemove())
    await send_create_ticket(message)


async def send_choice_category_admission(message: Message):
    await message.answer(texts.ticket.chosen_admission, reply_markup=ReplyKeyboardRemove())
    await send_create_ticket(message)


async def send_choice_privacy(message: Message):
    await message.answer(
        texts.ticket.choice_privacy,
        reply_markup=keyboards.choice_privacy_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.choice_privacy.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.choice_privacy)
async def handle_choice_privacy(message: Message, state: FSMContext):
    if message.text == texts.buttons.back:
        return await send_choice_category(message)

    if message.text == texts.buttons.no:
        async with state.proxy() as data:
            data[DATA_ANONYM_KEY] = True
        return await send_input_full_name(message)

    elif message.text == texts.buttons.yes:
        async with state.proxy() as data:
            data[DATA_ANONYM_KEY] = False
        return await send_input_text(message)

    await send_choice_privacy_invalid(message)


async def send_choice_privacy_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_button)
    await send_choice_privacy(message)


async def send_input_full_name(message: Message):
    await message.answer(
        texts.ticket.input_full_name,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.input_full_name.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.input_full_name)
async def handle_input_full_name(message: Message, state: FSMContext):
    words = message.text.split()
    if not (
        2 <= len(words) <= 3 and
        all(re.match(r"^[А-ЯЁа-яё\-]+$", word) for word in words)
    ):
        logger.info(f"Invalid input full name: {message.text}")
        return await send_input_full_name_invalid(message)
    full_name = []
    for word in words:
        if '-' in word:
            full_name.append('-'.join([small_w.capitalize() for small_w in word.split('-')]))
        else:
            full_name.append(word.capitalize())

    async with state.proxy() as data:
        data[DATA_FULL_NAME_KEY] = escape_swear_words(' '.join(full_name))
    await send_input_study_group(message)


async def send_input_full_name_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_full_name)
    await send_input_full_name(message)


async def send_input_study_group(message: Message):
    await message.answer(
        texts.ticket.input_study_group,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.input_study_group.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.input_study_group)
async def handle_input_study_group(message: Message, state: FSMContext):
    study_group = message.text.upper()
    if not validate_group(study_group):
        logger.info(f"Invalid input study group: {message.text}")
        return await send_input_study_group_invalid(message)
    async with state.proxy() as data:
        data[DATA_STUDY_GROUP_KEY] = study_group
    await send_input_text(message)


async def send_input_study_group_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_study_group)
    await send_input_study_group(message)


async def send_input_text(message: Message):
    await message.answer(
        texts.ticket.input_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.input_text.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.input_text)
async def handle_input_text(message: Message, state: FSMContext):
    text = escape_swear_words(message.html_text or message.text)
    async with state.proxy() as data:
        data[DATA_TEXT_KEY] = text
        if not data[DATA_ANONYM_KEY]:
            return await send_choice_approve(message)
    return await send_choice_processing_pd(message)


async def send_choice_processing_pd(message: Message):
    await message.answer(
        texts.ticket.choice_processing_pd,
        reply_markup=keyboards.choice_processing_pd_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.choice_processing_pd.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.choice_processing_pd)
async def handle_choice_approve(message: Message):
    if message.text == texts.buttons.yes:
        return await send_choice_approve(message)
    return await send_choice_processing_pd_invalid(message)


async def send_choice_processing_pd_invalid(message: Message):
    await message.answer(texts.errors.processing_pd_is_required)
    await send_choice_processing_pd(message)


async def send_choice_approve(message: Message):
    await message.answer(
        texts.ticket.choice_approve,
        reply_markup=keyboards.choice_approve_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await states.Registration.choice_approve.set()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=states.Registration.choice_approve)
async def handle_choice_approve(message: Message, state: FSMContext, store: Storage):
    if message.text == texts.buttons.yes:
        ticket = await save_ticket(message, state, store)
        content_message_id, meta_message_id = await send_ticket(ticket)
        await send_ticket_was_sent(message, ticket.id)
        await store.update_ticket(ticket.id, channel_content_message_id=content_message_id, channel_meta_message_id=meta_message_id)
    elif message.text == texts.buttons.no:
        return await send_choice_issue(message)
    else:
        await send_choice_approve_invalid(message)


async def send_choice_approve_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_button)
    await send_choice_approve(message)


async def save_ticket(message: Message, state: FSMContext, store: Storage) -> TicketRecord:
    async with state.proxy() as data:
        owner = None
        if data[DATA_ANONYM_KEY]:
            owner = domain.Student(
                full_name=data[DATA_FULL_NAME_KEY],
                study_group=data[DATA_STUDY_GROUP_KEY],
            )
        ticket = domain.Ticket(
            owner_chat_id=message.chat.id,
            issue=data[DATA_ISSUE_KEY],
            category=data[DATA_CATEGORY_KEY],
            text=data[DATA_TEXT_KEY],
            owner=owner,
            status=Status.OPENED,
        )
    return await store.save_ticket(ticket)


async def send_ticket(ticket: TicketRecord) -> tuple[int, int]:
    content = await bot.send_message(
        config.channel_chat_id,
        texts.ticket.ticket_content_message_channel(ticket),
        parse_mode=ParseMode.HTML)

    meta = await bot.send_message(
        config.channel_chat_id,
        texts.ticket.ticket_meta_message_channel(ticket),
        reply_markup=keyboards.keyboard_by_status(ticket.status, ticket.id))

    return content.message_id, meta.message_id


async def send_ticket_was_sent(message: Message, ticket_id: int):
    await message.answer(
        texts.ticket.ticket_sent(ticket_id),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    await send_create_ticket(message)


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state="*")
async def unknown(message: Message):
    if not message.reply_to_message:
        return await message.answer(texts.errors.no_reply)
    await message.answer(texts.errors.unknown)


def map_button_to_issue(btn: str) -> domain.Issue | None:
    match btn:
        case texts.buttons.question:
            return domain.Issue.QUESTION
        case texts.buttons.problem:
            return domain.Issue.PROBLEM
        case texts.buttons.suggestion:
            return domain.Issue.SUGGESTION
    return None


def map_button_to_category(btn: str) -> domain.Category | None:
    match btn:
        case texts.buttons.study:
            return domain.Category.STUDY
        case texts.buttons.dormitory:
            return domain.Category.DORMITORY
        case texts.buttons.food:
            return domain.Category.FOOD
        case texts.buttons.medicine:
            return domain.Category.MEDICINE
        case texts.buttons.military:
            return domain.Category.MILITARY
        case texts.buttons.admission:
            return domain.Category.ADMISSION
        case texts.buttons.documents:
            return domain.Category.DOCUMENTS
        case texts.buttons.scholarship:
            return domain.Category.SCHOLARSHIP
        case texts.buttons.electives:
            return domain.Category.ELECTIVES
        case texts.buttons.other:
            return domain.Category.OTHER
    return None


def validate_group(group_name: str) -> bool:
    regex = re.compile(r"^((((ФМОП-)?(ИУ|ИБМ|МТ|СМ|БМТ|РЛ|Э|РК|ФН|Л|СГН|ВУЦ|УЦ|ИСОТ|РКТ|АК|ПС|РТ|ЛТ|К|ЮР|ОЭ|ТА|ТБД|ТИ|ТД|ТИП|ТКС|ТМО|ТМР|ТР|ТСА|ТСР|ТСС|ТУ|ТУС|ТЭ)[1-9]\d?)|(ЮР(.ДК)?))(К)?[ИЦ]?-(((1[0-2])|(\d))((\d)|(.\d\d+))([АМБ]?(В)?)))$")
    return True if regex.match(group_name) else False
