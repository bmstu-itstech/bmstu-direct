import logging
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, IsReplyFilter
from aiogram.types import Message, ReplyKeyboardRemove, ParseMode, ChatType, ContentType

from core import texts
from core import states
from core import domain
from core.domain import TicketRecord, Status
from core.handlers import keyboards
from common.repository import dp, bot
from common.swear_words import escape_swear_words
from services.db.storage import Storage

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

@dp.message_handler(content_types=[
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
            ContentType.ANIMATION,  #GIF
        ], state="*")
async def handle_no_text(message:Message):
    await message.answer(
        texts.errors.message_no_text,
        parse_mode=ParseMode.HTML
    )

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), IsReplyFilter(is_reply=True), state="*")
async def handle_student_answer(message: Message, store: Storage):
    ticket_ids = await store.chat_ticket_ids(message.chat.id)
    replied_message = await store.message_by_id(
        ticket_ids=ticket_ids,
        owner_message_id=message.reply_to_message.message_id,
    )
    answer = escape_swear_words(message.text)
    await send_student_answer(message, store, replied_message, answer)


async def send_student_answer(message: Message, store: Storage, replied_message: domain.Message, answer: str):
    sent = await bot.send_message(
        config.comment_chat_id,
        texts.ticket.student_answer(answer),
        reply_to_message_id=replied_message.message_id,
        parse_mode=ParseMode.HTML,
    )
    await store.save_message(
        domain.Message(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            owner_message_id=message.message_id,
            reply_to_message_id=sent.reply_to_message.message_id,
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
        return await send_choice_category_military(message, state)
    if category is domain.Category.ADMISSION:
        return await send_choice_category_admission(message, state)
    async with state.proxy() as data:
        data[DATA_CATEGORY_KEY] = category
    await send_choice_privacy(message)


async def send_choice_category_invalid(message: Message):
    await message.answer(texts.errors.invalid_input_button)
    await send_choice_category(message)


async def send_choice_category_military(message: Message, state: FSMContext):
    await message.answer(texts.ticket.chosen_military, reply_markup=ReplyKeyboardRemove())
    await send_create_ticket(message)


async def send_choice_category_admission(message: Message, state: FSMContext):
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
    text = escape_swear_words(message.text)
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
        saved = await save_ticket(message, state, store)
        sent_id = await send_ticket(saved)
        await send_ticket_was_sent(message, saved.id)
        await store.update_ticket(saved.id, channel_message_id=sent_id)
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


async def send_ticket(ticket: TicketRecord) -> int:
    sent = await bot.send_message(
        config.channel_chat_id,
        texts.ticket.ticket_channel(ticket),
        parse_mode=ParseMode.HTML,
    )
    return sent.message_id


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
    regex = re.compile(r"^((((ФМОП-)?(ИУ|ИБМ|МТ|СМ|БМТ|РЛ|Э|РК|ФН|Л|СГН|ВУЦ|УЦ|ИСОТ|РКТ|АК|ПС|РТ|ЛТ|К|ЮР|ОЭ|ТА|ТБД|ТИ|ТД|ТИП|ТКС|ТМО|ТМР|ТР|ТСА|ТСР|ТСС|ТУ|ТУС|ТЭ)[1-9]\d?)|(ЮР))[ИЦ]?-(((1[0-2])|(\d))(\d)([АМБ]?(В)?)))$")
    return True if regex.match(group_name) else False
