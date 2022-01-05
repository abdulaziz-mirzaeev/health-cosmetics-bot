from telegram.ext import CallbackContext

RU = 'ru'
UZ = 'uz'

RU_BTN_LABEL = '🇷🇺 Русский'
UZ_BTN_LABEL = '🇺🇿 Ўзбек'

WELCOME_MESSAGE = 'Ассалому алайкум, ботимизга хуш келибсиз!\n' \
                  'Здравствуйте! Добро пожаловать в наш бот'

SELECT_LANG_MESSAGE = 'Илтимос, тилни танланг!\n' \
                      'Пожалуйста, выберите язык!'


messages = {
    RU: {
        'order': '🛍 Заказать',
        'cancel': '⬅️Назад',
        'cancel_universal': '⬅️',
        'enter_full_name': 'Введите свое имя и фамилию\n',
        'cool!Now': 'Замечательно! А теперь',
        'enter_phone_number': 'Введите ваш номер телефона\n'
                              'Например, +998*********',
        'select_category': 'Выберите категорию:',
        'select_product': 'Выберите продукт:',
        'select_from_options': 'Выберите из существующих опций',
        'thanks_for_filling': 'Спасибо, что вы заполнили анкету! '
                              'Специалисты в скором времени свяжутся с вами',
    },
    UZ: {
        'order': '🛍 Буюртма бериш',
        'cancel': '⬅️Орқага',
        'enter_full_name': 'Исм ва фамилиянгизни киритинг\n',
        'cool!Now': 'Ажойиб! Энди эса',
        'enter_phone_number': 'Телефон рақамингизни киритинг\n'
                              'Масалан, +998*********',
        'select_category': 'Категорияни танланг:',
        'select_product': 'Махсулотни танланг:',
        'select_from_options': 'Берилган опциялардан танланг',
        'thanks_for_filling': 'Сўровномани тўлдирганлигингиз учун рахмат!'
                              'Мутахасислар сиз билан тез орада боғланишади!',
    }
}


def getText(key, context: CallbackContext = None, lang=None):
    """
    Returns corresponding text according to given language
    on chat data of Context
    """
    if lang is None:
        lang = context.chat_data['lang']

    return messages[lang][key]
