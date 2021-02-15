#!/usr/bin/env python3
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    Dispatcher,
    InlineQueryHandler,
    CallbackQueryHandler,
)
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ParseMode,
)
import logging
import json
import settings
import requests
from uuid import uuid4

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)
updater = None


def satoshi_to_btc(satoshi: int):
    return format(float(satoshi * 0.00000001), ".8f")


def request(hash_: str = ""):
    response = requests.get(f"https://api.blockcypher.com/v1/btc/main/txs/{hash_}")
    return json.loads(response.text)


def generate_content(transaction):
    amount = satoshi_to_btc(transaction["total"])
    fee = satoshi_to_btc(transaction["fees"])
    total = format(float(amount) + float(fee), ".8f")
    fee_percent = round((float(fee) / float(total)) * 100, 2)
    confirmations = transaction["confirmations"]
    size = transaction["size"]
    hash_ = transaction["hash"]
    preference = transaction["preference"]
    inputs = len(transaction["inputs"])
    outputs = len(transaction["outputs"])
    date = transaction["received"].replace("T", " ").split(".")

    return (
        f"""Total amount: {total} BTC
Amount transacted: {amount} BTC
Fee: {fee} BTC ({fee_percent}% of total)
""",
        f"""Transaction hash: [{hash_}](https://live.blockcypher.com/btc/tx/{hash_})

Confirmations: *{confirmations}/6*

Total amount: *{total} BTC*
Amount transacted: *{amount} BTC*
Fee: *{fee} BTC* ({fee_percent}% of total)

Size: *{size} Bytes*
Preference: *{preference}*

Inputs: *{inputs}*
Outputs: *{outputs}*

Receive date: {date[0]} UTC
""",
    )


def inline(update, context):
    answers = []
    hash_ = str(update.inline_query.query)

    if hash_ == "":
        response = request()
        for transaction in response:
            description, content = generate_content(transaction)
            answers.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=transaction["hash"],
                    description=description,
                    input_message_content=InputTextMessageContent(
                        content,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Refresh", callback_data=transaction["hash"]
                                )
                            ]
                        ]
                    ),
                )
            )
        context.bot.answer_inline_query(update.inline_query.id, answers, cache_time=0)
    else:
        transaction = request(hash_)

        description, content = generate_content(transaction)
        answers.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=f'Bitcoin Transaction ({transaction["confirmations"]}/6)',
                description=description,
                input_message_content=InputTextMessageContent(
                    content,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Refresh", callback_data=transaction["hash"]
                            )
                        ]
                    ]
                ),
            )
        )
        context.bot.answer_inline_query(update.inline_query.id, answers, cache_time=0)


def refresh_data(update, context):
    query = update.callback_query
    transaction = request(query.data)
    _, content = generate_content(transaction)
    context.bot.edit_message_text(
        inline_message_id=query.inline_message_id,
        text=content,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refresh", callback_data=transaction["hash"])]]
        ),
    )


def start(update, context):
    update.message.reply_text(
        """
Bitcoin Transaction Tracking Bot

To use this bot start typing
@transaction_tracker_bot <transaction_hash>
or select transaction from list of latest transactions.
"""
    )


def main():
    global updater
    updater = Updater(settings.TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(["start", "help"], start))
    dispatcher.add_handler(InlineQueryHandler(inline))
    dispatcher.add_handler(CallbackQueryHandler(refresh_data))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
