import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from .db import add_watch, remove_watch, list_watches, get_last_price
from .moex import fetch_price_from_moex
import logging

logger = logging.getLogger(__name__)

class TickerStates(StatesGroup):
    waiting_for_ticker_add = State()
    waiting_for_ticker_remove = State()
    waiting_for_ticker_price = State()

def _main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ Добавить")],
        [KeyboardButton(text="📋 Список"), KeyboardButton(text="💹 Цена")],
    ], resize_keyboard=True)
    return kb

def _make_symbol_inline_keyboard(symbol: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Цена", callback_data=f"price:{symbol}"),
         InlineKeyboardButton(text="Удалить", callback_data=f"remove:{symbol}")]
    ])
    return kb

def register_handlers(dp: Dispatcher, bot: Bot):
    @dp.message(Command(commands=["start"]))
    async def cmd_start(message: Message):
        await message.answer(
            """Привет! Я бот для отслеживания акций с Московской биржи.
""",
            reply_markup=_main_keyboard()
        )

    @dp.message(Command(commands=["help"]))
    async def cmd_help(message: Message):
        await cmd_start(message)

    @dp.message(TickerStates.waiting_for_ticker_add)
    async def process_add_ticker(message: Message, state: FSMContext):
        symbol = (message.text or "").upper().strip()
        if not symbol:
            await message.reply("Пустой тикер. Попробуйте ещё раз.")
            return

        await message.reply(f"Проверяю тикер {symbol} на MOEX...")
        async with aiohttp.ClientSession() as session:
            price = await fetch_price_from_moex(symbol, session)

        if price is None:
            await message.reply("Не удалось найти тикер на MOEX или получить цену. Убедитесь, что тикер правильный.")
            await state.clear()
            return

        await add_watch(message.chat.id, symbol, price)
        await message.reply(f"Добавлено: <b>{symbol}</b>. Текущая цена: {price}", reply_markup=_main_keyboard())
        await state.clear()

    @dp.message(TickerStates.waiting_for_ticker_remove)
    async def process_remove_ticker(message: Message, state: FSMContext):
        symbol = (message.text or "").upper().strip()
        if not symbol:
            await message.reply("Пустой тикер. Попробуйте ещё раз.")
            return

        removed = await remove_watch(message.chat.id, symbol)
        if removed:
            await message.reply(f"{symbol} удалён из отслеживаемых.", reply_markup=_main_keyboard())
        else:
            await message.reply(f"{symbol} не найден в списке.", reply_markup=_main_keyboard())
        await state.clear()

    @dp.message(TickerStates.waiting_for_ticker_price)
    async def process_price_ticker(message: Message, state: FSMContext):
        symbol = (message.text or "").upper().strip()
        if not symbol:
            await message.reply("Пустой тикер. Попробуйте ещё раз.")
            return

        await message.reply("Запрашиваю цену...")
        async with aiohttp.ClientSession() as session:
            price = await fetch_price_from_moex(symbol, session)

        if price is None:
            await message.reply("Не удалось получить цену для " + symbol, reply_markup=_main_keyboard())
        else:
            await message.reply(f"{symbol}: {price}", reply_markup=_main_keyboard())
        await state.clear()

    @dp.callback_query()
    async def cb_query_all(cb: CallbackQuery, state: FSMContext):
        data = cb.data or ""
        if data.startswith("price:"):
            symbol = data.split(":", 1)[1]
            await cb.answer()
            async with aiohttp.ClientSession() as session:
                price = await fetch_price_from_moex(symbol, session)
            if price is None:
                await cb.message.answer(f"Не удалось получить цену для {symbol}")
            else:
                await cb.message.edit_text(f"{symbol} : {('%.4g' % price) if price is not None else '—'}", reply_markup=_make_symbol_inline_keyboard(symbol))
            return
        if data.startswith("remove:"):
            symbol = data.split(":", 1)[1]
            await cb.answer()
            removed = await remove_watch(cb.message.chat.id, symbol)
            if removed:
                await cb.message.answer(f"{symbol} удалён из отслеживаемых.")
            else:
                await cb.message.answer(f"{symbol} не найден в списке.")
            return

    @dp.message()
    async def all_text_handler(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            return

        text = (message.text or "").strip()
        if text == "➕ Добавить":
            await message.answer("Отправь тикер для добавления (например SBER или GAZP):")
            await state.set_state(TickerStates.waiting_for_ticker_add)
            return
        if text == "➖ Удалить":
            await message.answer("Отправь тикер для удаления (например SBER):")
            await state.set_state(TickerStates.waiting_for_ticker_remove)
            return
        if text == "📋 Список":
            items = await list_watches(message.chat.id)
            if not items:
                await message.answer("Список пуст. Добавьте тикер через кнопку ➕")
                return
            for sym, price in items:
                kb = _make_symbol_inline_keyboard(sym)
                await message.answer(f"{sym} : {('%.4g' % price) if price is not None else '—'}", reply_markup=kb)
            return
        if text == "💹 Цена":
            await message.answer("Отправь тикер, для которого нужно получить цену:")
            await state.set_state(TickerStates.waiting_for_ticker_price)
            return