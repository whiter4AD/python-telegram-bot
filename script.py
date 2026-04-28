import logging
import os
import psycopg2
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота и БД из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
BOT_USERNAME = os.getenv('BOT_USERNAME', '')  # для формирования реферальной ссылки

# ID администратора
ADMIN_IDS = {7602351348}

# Часовой пояс бота (GMT+5)
BOT_TZ = timezone(timedelta(hours=5))


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Реквизиты для оплаты
PAYMENT_DETAILS = {
    'trc20': '🪙 trc20: TRQr75osx6tdhV3s9J9A3LhRrY5YRNmVgr',
}

# База данных товаров
PRODUCTS = {
    '📱 Argentina': {
        'name': '📱 Аргентина',
        'items': {
            'Personal': {'name': 'Personal Bank', 'price': 65, 'desc': 'Карта данного банка'},
            'Ripio': {'name': 'Ripio Bank', 'price': 65, 'desc': 'Карта данного банка'},
            'Buendit': {'name': 'Buendit Bank', 'price': 65, 'desc': 'Карта данного банка'},
            'BrueBank': {'name': 'Brue Bank', 'price': 60, 'desc': 'Карта данного банка'},
            'ClaroPay': {'name': 'ClaroPay Bank', 'price': 75, 'desc': 'Карта данного банка'},
            'Mercado Pagos': {'name': 'Mercado Pagos Bank', 'price': 100, 'desc': 'Карта данного банка'},
            'Dolarapp': {'name': 'Dolarapp Bank', 'price': 65, 'desc': 'Карта данного банка'},
            'Naranjia': {'name': 'Naranjia Bank', 'price': 100, 'desc': 'Карта данного банка'},
            'LemonCash': {'name': 'LemonCash Bank', 'price': 100, 'desc': 'Карта данного банка'},
            'Cocos': {'name': 'Cocos Bank', 'price': 95, 'desc': 'Карта данного банка'},
            'Global': {'name': 'Global Bank', 'price': 65, 'desc': 'Карта данного банка'},
            'Albo': {'name': 'Albo Bank', 'price': 80, 'desc': 'Карта данного банка'},
            'Uala': {'name': 'Uala Bank', 'price': 75, 'desc': 'Карта данного банка'},
            'Jeton': {'name': 'Jeton Bank', 'price': 70, 'desc': 'Карта данного банка'},
            'P100': {'name': 'P100 Bank', 'price': 75, 'desc': 'Карта данного банка'},
            'Majority': {'name': 'Majority Bank', 'price': 75, 'desc': 'Карта данного банка'},
            'Takenos': {'name': 'Takenos Bank', 'price': 75, 'desc': 'Карта данного банка'},
        }
    },
    '🔥 Turkey': {
        'name': '🔥 Турция',
        'items': {
            'OnMobil': {'name': 'OnMobil Bank', 'price': 135, 'desc': 'Карта данного банка'},
            'lussi Wallet': {'name': 'Luziko Bank', 'price': 90, 'desc': 'Карта данного банка'},
            'Hadi': {'name': 'не вериф Hadi Bank', 'price': 13, 'desc': 'Карта данного банка'},
            'Sipay Verifed': {'name': 'Sipay Verifed Bank', 'price': 90, 'desc': 'Карта данного банка'},
            'Turan': {'name': 'Turan Bank', 'price': 95, 'desc': 'Карта данного банка'},
            'Moneytolia': {'name': 'Moneytolia Bank', 'price': 95, 'desc': 'Карта данного банка'},
            'Fups Prem': {'name': 'Fups Prem Bank', 'price': 100, 'desc': 'Карта данного банка'},
            'Uption': {'name': 'Uption Bank', 'price': 120, 'desc': 'Карта данного банка'},
            'AhlPay': {'name': 'AhlPay Bank', 'price': 120, 'desc': 'Карта данного банка'},
            'HayHay': {'name': 'HayHay Bank', 'price': 120, 'desc': 'Карта данного банка'},
            'eSim Turkcell/VodaFone': {'name': 'eSim', 'price': 100, 'desc': 'Turkey eSim'},
        }
    },
    '🛡️ Crypto exchanges': {
        'name': '🛡️ Верификация',
        'items': {
            'Bybit': {'name': 'Bybit 2lvl + card', 'price': 45, 'desc': 'Верификация'},
            'OKX': {'name': 'OKX', 'price': 25, 'desc': 'Верификация'},
            'Mexc': {'name': 'Mexc', 'price': 25, 'desc': 'Верификация'},
            'Fragment': {'name': 'Fragment', 'price': 25, 'desc': 'Верификация'},
            'Binance': {'name': 'Binance', 'price': 25, 'desc': 'Верификация'},
            'HTX': {'name': 'HTX', 'price': 25, 'desc': 'Верификация'},
            'BetBoom': {'name': 'BetBoom', 'price': 25, 'desc': 'Верификация'},
            'Faceit': {'name': 'Faceit', 'price': 15, 'desc': 'Верификация'},
            'Cryptobot': {'name': 'Cryptobot', 'price': 20, 'desc': 'Верификация'},
        }
    },
    '🎯 India': {
        'name': '🎯 Индия',
        'items': {
            'Slice': {'name': 'Slice Bank', 'price': 270, 'desc': 'Карта данного банка'},
            'Airtel Payment': {'name': 'Airtel Payment Bank', 'price': 185, 'desc': 'Карта данного банка'},
            'Unity': {'name': 'Unity Bank', 'price': 270, 'desc': 'Карта данного банка'},
            'Fino': {'name': 'Fino Bank', 'price': 180, 'desc': 'Карта данного банка'},
            'NSDL': {'name': 'NSDL Bank', 'price': 215, 'desc': 'Карта данного банка'},
            'Кошелёк Dhani': {'name': 'Dhani Wallet', 'price': 95, 'desc': 'Кошелёк'},
            'eSim VI/Airtel': {'name': 'eSim', 'price': 60, 'desc': 'India eSim'},
        }
    },
    '🍩 Nigeria': {
        'name': '🍩 Нигерия',
        'items': {
            'Kuda': {'name': 'Kuda Bank', 'price': 50, 'desc': 'Карта данного банка'},
            'Moniepoint': {'name': 'Moniepoint Bank', 'price': 85, 'desc': 'Карта данного банка'},
            'Paga USD': {'name': 'Paga USD Bank', 'price': 55, 'desc': 'Карта данного банка'},
            'Opay': {'name': 'Opay Bank', 'price': 125, 'desc': 'Карта данного банка'},
            'Chipper Cash': {'name': 'Chipper Cash Bank', 'price': 50, 'desc': 'Карта данного банка'},
            'Go Money': {'name': 'Go Money Bank', 'price': 50, 'desc': 'Карта данного банка'},
            'Timon': {'name': 'Timon Bank', 'price': 70, 'desc': 'Карта данного банка'},
            'Alt': {'name': 'Alt Bank', 'price': 70, 'desc': 'Карта данного банка'},
            'First': {'name': 'First Bank', 'price': 125, 'desc': 'Карта данного банка'},
            'Access More': {'name': 'Access More Bank', 'price': 125, 'desc': 'Карта данного банка'},
            'eSim MTN': {'name': 'eSim', 'price': 30, 'desc': 'Nigeria eSim'},
        }
    },
    '💥 Kazakhstan': {
        'name': '💥 Казахстан',
        'items': {
            'Kaspi': {'name': 'Kaspi Bank', 'price': 150, 'desc': 'Карта данного банка'},
            'Tayyab': {'name': 'Tayyab Bank', 'price': 210, 'desc': 'Карта данного банка'},
            'Hodl': {'name': 'Hodl Bank', 'price': 350, 'desc': 'Карта данного банка'},
            'eSim Kazakhstan': {'name': 'eSim', 'price': 30, 'desc': 'Kazakhstan eSim'},
        }
    },
    '💰 Multicurrency': {   
        'name': '💰 Мультиватютки',
        'items': {
            'Armenia': {'name': 'Armenia Bank', 'price': 470, 'desc': 'Международная именная карта MASTERCARD банка Армении'},
            'Armenia Signature': {'name': 'Armenia Signature Bank', 'price': 840, 'desc': 'Международная именная карта VISA банка Армении'},
            'Kyrgyzstan': {'name': 'Kyrgyzstan Bank', 'price': 640, 'desc': 'Международная именная карта Visa банка Кыргызстана'},
            'KZ Global': {'name': 'KZ Global Bank', 'price': 320, 'desc': 'Набор из 3 именных VISA/MASTERCARD карт'}
        }
    }
}

# Корзина и заказы (в памяти)
carts = {}
orders = {}
user_consent = {}


def get_main_keyboard():
    buttons = [
        [KeyboardButton('📋 Каталог'), KeyboardButton('🛒 Корзина')],
        [KeyboardButton('💳 Реквизиты'), KeyboardButton('❓ Помощь')],
        [KeyboardButton('📞 Контакты')],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


# ── База данных ───────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_database():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT,
            referrer_id BIGINT
        )
    ''')
    # На случай уже существующей таблицы — добавляем колонку, если её нет
    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referrer_id BIGINT")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id BIGINT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()


def add_user_to_db(user_id, username, first_name):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, joined_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        ''', (user_id, username, first_name, datetime.now(BOT_TZ).strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        conn.close()


def get_total_users():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_user_ids():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def get_recent_users(limit=10):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, joined_date FROM users ORDER BY joined_date DESC LIMIT %s", (limit,))
    users = cursor.fetchall()
    conn.close()
    return users


def block_user_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO blocked_users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            (user_id,),
        )
        conn.commit()
    finally:
        conn.close()


def unblock_user_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM blocked_users WHERE user_id = %s", (user_id,))
        conn.commit()
    finally:
        conn.close()


def is_user_blocked(user_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blocked_users WHERE user_id = %s", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None


async def check_blocked(update: Update) -> bool:
    """Проверяем, заблокирован ли пользователь. Если да — сообщаем и возвращаем True."""
    user = update.effective_user
    if not user:
        return False
    if is_admin(user.id):
        return False

    if not is_user_blocked(user.id):
        return False

    if update.callback_query:
        await update.callback_query.answer("⛔ Доступ к боту ограничен.", show_alert=True)
    elif update.message:
        await update.message.reply_text("⛔ Доступ к боту ограничен.")
    return True


# ── Хендлеры ─────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    user = update.effective_user
    add_user_to_db(user.id, user.username, user.first_name)

    if user.id not in user_consent or not user_consent[user.id]:
        keyboard = [
            [InlineKeyboardButton("📜 Прочитать условия", url="https://telegra.ph/DivineStore-04-26")],
            [InlineKeyboardButton("✅ Я принимаю условия", callback_data='accept_terms')]
        ]
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n📜 Пожалуйста, ознакомьтесь с условиями работы по ссылке ниже.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\nДоступные команды:\n"
            "/catalog - 📋 Каталог\n/cart - 🛒 Корзина\n/payment - 💳 Реквизиты\n/help - ❓ Помощь\n/contact - 📞 Контакты"
        , reply_markup=get_main_keyboard())


async def accept_terms(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_consent[user.id] = True
    await query.edit_message_text(
        f"✅ Условия приняты.\n\n👋 Привет, {user.first_name}!\n\n"
        "/catalog - 📋 Каталог\n/cart - 🛒 Корзина\n/payment - 💳 Реквизиты\n/help - ❓ Помощь\n/contact - 📞 Контакты"
    )
    # Отправляем отдельным сообщением главное меню с постоянной клавиатурой
    await query.message.reply_text("🏠 Главное меню:", reply_markup=get_main_keyboard())


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    await update.message.reply_text(
        "❓ Помощь:\n\n"
        "1. /catalog - каталог товаров\n"
        "2. Выберите категорию и товар\n"
        "3. Добавьте в корзину\n"
        "4. /cart - проверьте корзину\n"
        "5. Оплатите и отправьте скриншот менеджеру\n\n"
        "/contact - контакты"
    , reply_markup=get_main_keyboard())


async def contact(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    await update.message.reply_text(
        "📞 Контакты:\n\nEmail: divinestoreofficial@duck.com\nTelegram: @SwagExxxchange\n\nРежим работы: Пн-Вс 10:00 - 22:00 мск",
        reply_markup=get_main_keyboard()
    )


async def handle_contact(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 Контакты:\n\nEmail: divinestoreofficial@duck.com\nTelegram: @SwagExxxchange\n\nРежим работы: Пн-Вс 10:00 - 22:00 мск",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🏠 В главное меню', callback_data='main_menu')]])
    )


async def show_payment_details(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    text = (
        f"💳 Реквизиты для оплаты:\n\n"
        f"{PAYMENT_DETAILS['trc20']}\n\n"
        "📌 После оплаты:\n1. Сохраните чек\n2. Напишите менеджеру: @SwagExxxchange"
    )
    keyboard = [
        [InlineKeyboardButton('📋 Корзина', callback_data='show_cart')],
        [InlineKeyboardButton('📞 Менеджер', callback_data='contact')],
        [InlineKeyboardButton('🏠 Меню', callback_data='main_menu')]
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def catalog(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'category_{k}')] for k, v in PRODUCTS.items()]
    await update.message.reply_text("📋 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_catalog(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'category_{k}')] for k, v in PRODUCTS.items()]
    await query.edit_message_text("📋 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))


async def back_to_catalog(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'category_{k}')] for k, v in PRODUCTS.items()]
    await query.edit_message_text("📋 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_category(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    category_id = query.data.replace('category_', '')
    category = PRODUCTS[category_id]
    keyboard = [
        [InlineKeyboardButton(f"{item['name']} - {item['price']}$", callback_data=f'item_{category_id}_{item_id}')]
        for item_id, item in category['items'].items()
    ]
    keyboard.append([InlineKeyboardButton('◀️ Назад', callback_data='back_to_catalog')])
    await query.edit_message_text(f"{category['name']}:\nВыберите товар:", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_item(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    _, category_id, item_id = query.data.split('_', 2)
    item = PRODUCTS[category_id]['items'][item_id]
    keyboard = [
        [InlineKeyboardButton('🛒 Добавить в корзину', callback_data=f'add_{category_id}_{item_id}')],
        [InlineKeyboardButton('◀️ Назад', callback_data=f'category_{category_id}')],
        [InlineKeyboardButton('🏠 Каталог', callback_data='back_to_catalog')]
    ]
    await query.edit_message_text(
        f"{item['name']}\n\n📝 {item['desc']}\n💰 Цена: {item['price']}$",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_to_cart(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    _, category_id, item_id = query.data.split('_', 2)
    if user_id not in carts:
        carts[user_id] = []
    carts[user_id].append({'category_id': category_id, 'item_id': item_id})
    await query.edit_message_text(
        "✅ Товар добавлен в корзину!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🛒 Корзина', callback_data='show_cart')],
            [InlineKeyboardButton('📋 Продолжить', callback_data='back_to_catalog')]
        ])
    )


async def show_cart(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.message.chat_id

    cart_items = carts.get(user_id, [])

    if not cart_items:
        text = "🛒 Корзина пуста!"
        keyboard = [[InlineKeyboardButton('📋 Каталог', callback_data='back_to_catalog')]]
    else:
        total = 0
        text = "🛒 Ваша корзина:\n\n"
        for i, item in enumerate(cart_items, 1):
            product = PRODUCTS[item['category_id']]['items'][item['item_id']]
            text += f"{i}. {product['name']} - {product['price']}$\n"
            total += product['price']
        text += f"\n💰 Итого: {total}$"
        order_id = f"#{user_id}_{len(orders) + 1}"
        keyboard = [
            [InlineKeyboardButton('✅ Оплатить', callback_data=f'pay_{order_id}')],
            [InlineKeyboardButton('🗑 Очистить', callback_data='clear_cart')],
            [InlineKeyboardButton('📋 Продолжить', callback_data='back_to_catalog')]
        ]

    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def clear_cart(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    carts[query.from_user.id] = []
    await query.edit_message_text(
        "🗑 Корзина очищена!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📋 Каталог', callback_data='back_to_catalog')]])
    )


async def process_payment(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    _, order_id = query.data.split('_', 1)
    cart_items = carts.get(user_id, [])

    if not cart_items:
        await query.edit_message_text("❌ Корзина пуста!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📋 Каталог', callback_data='back_to_catalog')]]))
        return

    total = sum(PRODUCTS[i['category_id']]['items'][i['item_id']]['price'] for i in cart_items)
    orders[order_id] = {'user_id': user_id, 'items': cart_items.copy(), 'status': 'pending', 'total_price': total}

    text = (
        f"🧾 Заказ {order_id}\n\n💰 Сумма: {total}$\n\n💳 Реквизиты:\n\n"
        f"{PAYMENT_DETAILS['trc20']}\n\n"
        "📌 После оплаты нажмите кнопку ниже и отправьте скриншот менеджеру."
    )
    keyboard = [
        [InlineKeyboardButton('✅ Я оплатил', callback_data=f'confirm_{order_id}')],
        [InlineKeyboardButton('📞 Менеджер', callback_data='contact')],
        [InlineKeyboardButton('📋 Каталог', callback_data='back_to_catalog')]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    _, order_id = query.data.split('_', 1)
    user_id = query.from_user.id

    if order_id not in orders:
        await query.edit_message_text("❌ Заказ не найден.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📞 Менеджер', callback_data='contact')]]))
        return

    orders[order_id]['status'] = 'paid'
    items_text = "\n".join(
        f"• {PRODUCTS[i['category_id']]['items'][i['item_id']]['name']} - {PRODUCTS[i['category_id']]['items'][i['item_id']]['price']}$"
        for i in orders[order_id]['items']
    )

    try:
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 Новая оплата!\n\nЗаказ: {order_id}\nПользователь: @{query.from_user.username} (ID: {user_id})\nСумма: {orders[order_id]['total_price']}$\n\nТовары:\n{items_text}"
            )
    except Exception:
        logger.warning("Не удалось отправить уведомление менеджеру")

    carts[user_id] = []
    await query.edit_message_text(
        f"✅ Спасибо за оплату!\n\nЗаказ {order_id} отмечен как оплаченный.\nМенеджер проверит поступление и свяжется с вами.\n\n📞 @SwagExxxchange",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('📞 Менеджер', callback_data='contact')],
            [InlineKeyboardButton('🏠 Меню', callback_data='main_menu')]
        ])
    )


async def main_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if await check_blocked(update):
        return
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton('📋 Каталог', callback_data='show_catalog')],
        [InlineKeyboardButton('🛒 Корзина', callback_data='show_cart')],
        [InlineKeyboardButton('💳 Реквизиты', callback_data='show_payment')],
        [InlineKeyboardButton('📞 Контакты', callback_data='contact')]
    ]
    await query.edit_message_text("🏠 Главное меню:", reply_markup=InlineKeyboardMarkup(keyboard))


async def admin_panel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Нет доступа.")
        return
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("📢 Рассылка", callback_data='admin_broadcast')],
        [InlineKeyboardButton("👥 Пользователи", callback_data='admin_users')],
        [InlineKeyboardButton("🚫 Блокировка", callback_data='admin_block_menu')],
    ]
    await update.message.reply_text("🔐 Админ панель:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def admin_stats(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.edit_message_text("⛔ Доступ запрещен.")
        return
    total = get_total_users()
    await query.edit_message_text(
        f"📊 Статистика\n\n👥 Всего пользователей: {total}\n📅 {datetime.now(BOT_TZ).strftime('%d.%m.%Y %H:%M')}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data='back_to_admin')]])
    )


async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    context.user_data['awaiting_broadcast'] = True
    await query.edit_message_text("📢 Режим рассылки\n\nОтправь сообщение для рассылки. Для отмены: /cancel")


async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or not context.user_data.get('awaiting_broadcast'):
        return
    users = get_all_user_ids()
    context.user_data['broadcast_message'] = {
        # Сохраняем исходное сообщение, чтобы копировать его (premium-эмодзи и форматирование сохраняются)
        'chat_id': update.message.chat_id,
        'message_id': update.message.message_id,
    }
    keyboard = [[
        InlineKeyboardButton("✅ Подтвердить", callback_data='confirm_broadcast'),
        InlineKeyboardButton("❌ Отменить", callback_data='cancel_broadcast')
    ]]
    await update.message.reply_text(
        f"📢 Предпросмотр рассылки\n\nБудет отправлено: {len(users)} пользователям",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['awaiting_broadcast'] = False


async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    await query.edit_message_text("⏳ Рассылка начата...")
    users = get_all_user_ids()
    msg = context.user_data.get('broadcast_message', {})
    src_chat_id = msg.get('chat_id')
    src_message_id = msg.get('message_id')
    successful, failed = 0, 0
    for (uid,) in users:
        try:
            # Копируем оригинальное сообщение, чтобы сохранить premium-эмодзи, форматирование и кнопки
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=src_chat_id,
                message_id=src_message_id,
            )
            successful += 1
        except Exception:
            failed += 1
    await query.message.edit_text(
        f"✅ Рассылка завершена!\n\n📊 Всего: {len(users)}\n✅ Успешно: {successful}\n❌ Ошибок: {failed}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data='back_to_admin')]])
    )


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting_broadcast'] = False
    context.user_data['broadcast_message'] = None
    await query.edit_message_text("❌ Рассылка отменена.")


async def admin_users_list(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    users = get_recent_users()
    text = "👥 Последние 10 пользователей:\n\n"
    for uid, username, first_name, joined in users:
        text += f"• {first_name} (@{username or 'нет'})\n  ID: {uid}\n  Дата: {joined}\n\n"
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data='back_to_admin')]])
    )


async def admin_block_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Небольшая подсказка по блокировке пользователей."""
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    text = (
        "🚫 Блокировка пользователей\n\n"
        "Используйте команды:\n"
        "/block <user_id> — заблокировать пользователя\n"
        "/unblock <user_id> — разблокировать пользователя"
    )
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data='back_to_admin')]])
    )


async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Нет доступа.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Использование: /block <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID пользователя должен быть числом.")
        return
    block_user_db(target_id)
    await update.message.reply_text(f"🚫 Пользователь {target_id} заблокирован.")


async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Нет доступа.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Использование: /unblock <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID пользователя должен быть числом.")
        return
    unblock_user_db(target_id)
    await update.message.reply_text(f"✅ Пользователь {target_id} разблокирован.")


async def back_to_admin(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("📢 Рассылка", callback_data='admin_broadcast')],
        [InlineKeyboardButton("👥 Пользователи", callback_data='admin_users')],
    ]
    await query.edit_message_text("🔐 Админ панель:", reply_markup=InlineKeyboardMarkup(keyboard))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_broadcast'):
        context.user_data['awaiting_broadcast'] = False
        await update.message.reply_text("❌ Режим рассылки отменен.")
    else:
        await update.message.reply_text("❌ Нет активного действия.")


async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обрабатываем только сообщения админа и только в режиме ожидания текста рассылки
    if update.effective_user and is_admin(update.effective_user.id) and context.user_data.get('awaiting_broadcast'):
        await handle_broadcast_message(update, context)


def main():
    init_database()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("cart", show_cart))
    application.add_handler(CommandHandler("payment", show_payment_details))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("block", block_user))
    application.add_handler(CommandHandler("unblock", unblock_user))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(CallbackQueryHandler(accept_terms, pattern='^accept_terms$'))
    application.add_handler(CallbackQueryHandler(show_category, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(show_item, pattern='^item_'))
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern='^add_'))
    application.add_handler(CallbackQueryHandler(show_cart, pattern='^show_cart$'))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern='^clear_cart$'))
    application.add_handler(CallbackQueryHandler(process_payment, pattern='^pay_'))
    # подтверждение оплаты: callback_data имеет вид confirm_#userId_N, поэтому добавляем #,
    # чтобы не перехватывать другие confirm_* (например, confirm_broadcast)
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern='^confirm_#'))
    application.add_handler(CallbackQueryHandler(show_payment_details, pattern='^show_payment$'))
    application.add_handler(CallbackQueryHandler(handle_contact, pattern='^contact$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(show_catalog, pattern='^show_catalog$'))
    application.add_handler(CallbackQueryHandler(back_to_catalog, pattern='^back_to_catalog$'))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern='^admin_stats$'))
    application.add_handler(CallbackQueryHandler(admin_broadcast_start, pattern='^admin_broadcast$'))
    application.add_handler(CallbackQueryHandler(admin_users_list, pattern='^admin_users$'))
    application.add_handler(CallbackQueryHandler(admin_block_menu, pattern='^admin_block_menu$'))
    application.add_handler(CallbackQueryHandler(confirm_broadcast, pattern='^confirm_broadcast$'))
    application.add_handler(CallbackQueryHandler(cancel_broadcast, pattern='^cancel_broadcast$'))
    application.add_handler(CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$'))
    # Текстовые кнопки главного меню (без слеша)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^📋 Каталог$'), catalog))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^🛒 Корзина$'), show_cart))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^💳 Реквизиты$'), show_payment_details))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^❓ Помощь$'), help_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^📞 Контакты$'), contact))
    # Хендлер для сообщений, используемых в режиме рассылки (любой тип, кроме команд)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_all_messages))

    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
