import sys

from django.db.models import Q

from messages import RU_BTN_LABEL, UZ, RU, UZ_BTN_LABEL, WELCOME_MESSAGE, SELECT_LANG_MESSAGE, getText

sys.dont_write_bytecode = True

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

from db.models import Person, Product, Category

from telegram.ext import \
    (
     Updater,
     Dispatcher,
     ConversationHandler,
     CommandHandler,
     CallbackContext,
     MessageHandler,
     Filters
    )
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup, InputMediaPhoto
import logging

LANGUAGE, FULL_NAME, PHONE_NUMBER, CATEGORY, PRODUCT_SELECT, PRODUCT = range(6)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_product_menu_keyboard(category_id):
    products: Product = Product.objects.filter(category_id=category_id)
    reply_keyboard = map(lambda x: KeyboardButton(x.title), products)
    keyboard = list(chunks(list(reply_keyboard), 2))
    keyboard.append([KeyboardButton(getText('cancel', lang=RU))])
    return keyboard


def get_product_menu_options():
    products: Product = Product.objects.all()
    options = []
    for productI in products:
        options.append(productI.title)
    return '|'.join(options)


def get_category_menu_keyboard(lang):
    categories = Category.objects.all()
    attribute = 'title_' + lang
    reply_keyboard = map(
        lambda x: KeyboardButton(getattr(x, attribute, 'title_uz')),
        categories
    )
    return reply_keyboard


def get_category_menu_options():
    categories = Category.objects.all()
    options = []
    for category in categories:
        options.append(category.title_ru)
        options.append(category.title_uz)
    return '|'.join(options)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )
    lang_buttons = [RU_BTN_LABEL, UZ_BTN_LABEL]
    update.message.reply_text(
        SELECT_LANG_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            [lang_buttons], resize_keyboard=True, one_time_keyboard=True,
        )
    )
    return LANGUAGE


def language(update: Update, context: CallbackContext):
    lang = ''
    if update.message.text == f'{RU_BTN_LABEL}':
        lang = RU
    elif update.message.text == f'{UZ_BTN_LABEL}':
        lang = UZ

    context.chat_data.update({
        'lang': lang
    })

    update.message.reply_text(
        getText('enter_full_name', context),
        reply_markup=ReplyKeyboardRemove()
    )
    return FULL_NAME


def language_resend(update: Update, context: CallbackContext):
    lang_buttons = [RU_BTN_LABEL, UZ_BTN_LABEL]
    update.message.reply_text(
        SELECT_LANG_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            [lang_buttons], resize_keyboard=True, one_time_keyboard=True,
        )
    )
    return LANGUAGE


def full_name(update: Update, context: CallbackContext):
    context.chat_data.update({
        'full_name': update.message.text
    })

    update.message.reply_text(
        getText('cool!Now', context)
    )
    update.message.reply_text(
        getText('enter_phone_number', context)
    )

    return PHONE_NUMBER


def phone_number(update: Update, context: CallbackContext):
    context.chat_data.update({
        'phone_number': update.message.text
    })
    reply_keyboard = get_category_menu_keyboard(context.chat_data['lang'])

    update.message.reply_text(
        getText('select_category', context),
        reply_markup=ReplyKeyboardMarkup(
            [reply_keyboard], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return CATEGORY


def category(update: Update, context: CallbackContext):
    selected_category = update.message.text
    category_id = Category.objects.get(Q(title_uz=selected_category) | Q(title_ru=selected_category)).id
    context.chat_data.update({
        'category_id': category_id
    })
    reply_keyboard = get_product_menu_keyboard(category_id)

    update.message.reply_text(
        getText('select_product', context),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return PRODUCT_SELECT


def category_resend(update: Update, context: CallbackContext):
    reply_keyboard = get_category_menu_keyboard(context.chat_data['lang'])

    update.message.reply_text(
        getText('select_category', context),
        reply_markup=ReplyKeyboardMarkup(
            [reply_keyboard], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return CATEGORY


def product_select(update: Update, context: CallbackContext):
    product_object: Product = Product.objects.get(title=update.message.text)

    context.chat_data.update({
        'product': update.message.text
    })
    photo_caption = f'{product_object.description_uz}'

    update.message.reply_photo(
        photo=open(f'.{product_object.img_url}', 'rb'),
        caption=photo_caption,
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton(
                getText('order', context)
            )],
            [KeyboardButton(
                getText('cancel', context)
            )]
        ], resize_keyboard=True, one_time_keyboard=True),

    )

    return PRODUCT


def product_select_cancel(update: Update, context: CallbackContext):
    reply_keyboard = get_category_menu_keyboard(context.chat_data['lang'])

    update.message.reply_text(
        getText('select_category', context),
        reply_markup=ReplyKeyboardMarkup(
            [reply_keyboard], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return CATEGORY


def product_cancel(update: Update, context: CallbackContext):
    reply_keyboard = get_product_menu_keyboard(context.chat_data['category_id'])

    update.message.reply_text(
        getText('select_product', context),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return PRODUCT_SELECT


def product_resend(update: Update, context: CallbackContext):
    update.message.reply_text(
        getText('select_from_options', context)
    )
    return PRODUCT


def product(update: Update, context: CallbackContext):
    cd = context.chat_data

    person = Person.objects.create(
        full_name=cd['full_name'],
        phone_number=cd['phone_number'],
        product=cd['product'],
        user_id=update.effective_user.id,
    )
    update.message.reply_text(
        getText('thanks_for_filling', context),
        reply_markup=ReplyKeyboardRemove()
    )

    context.bot.send_message(
        '@health_bot_channel',
        f'Имя: {person.full_name}\n'
        f'Номер телефона: {person.phone_number}\n'
        f'Продукт: {person.product}',
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        getText('thanks_for_filling', context),
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    """Run the Bot"""
    updater: Updater = Updater(token='5093206396:AAGBWNO7euljUuKSXmCjl3BZiWdrF5tBduU')

    dispatcher: Dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                MessageHandler(Filters.regex(f'^{RU_BTN_LABEL}|{UZ_BTN_LABEL}$'), language),
                MessageHandler(Filters.all, language_resend),
            ],
            FULL_NAME: [MessageHandler(Filters.text, full_name)],
            PHONE_NUMBER: [MessageHandler(Filters.contact | Filters.text, phone_number)],
            CATEGORY: [
                MessageHandler(Filters.regex(f'^({get_category_menu_options()})$'), category),
                MessageHandler(Filters.all, category_resend)
            ],
            PRODUCT_SELECT: [
                MessageHandler(Filters.regex(f'^({get_product_menu_options()})$'), product_select),
                MessageHandler(Filters.regex(f'^{getText("cancel", lang=RU)}$'), product_select_cancel)
            ],
            PRODUCT: [
                MessageHandler(
                    Filters.regex(f'^{getText("order", lang="uz")}|{getText("order", lang="ru")}$'), product
                ),
                MessageHandler(
                    Filters.regex(f'^{getText("cancel", lang="uz")}|{getText("cancel", lang="ru")}$'), product_cancel
                ),
                MessageHandler(Filters.all, product_resend)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
