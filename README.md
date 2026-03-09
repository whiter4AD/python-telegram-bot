# Telegram Shop Bot — python-telegram-bot + PostgreSQL

Telegram бот для продажи цифровых товаров с корзиной, админ-панелью и PostgreSQL.

## Stack

* **python-telegram-bot 20.7** — Telegram Bot API framework
* **PostgreSQL** — база данных пользователей
* **psycopg2-binary** — PostgreSQL adapter
* **Railway** — хостинг и деплой

## Project Structure

telegram-shop-bot/
├── bot.py # Основной код бота (все хендлеры + админка)
├── requirements.txt # Зависимости
└── README.md
text


## Features

### Для покупателей
* 📋 **Каталог товаров** — 5+ категорий
* 🛒 **Корзина** — добавление/удаление, подсчет суммы
* 💳 **Реквизиты** — карта, банк, TRC20
* ✅ **Согласие с условиями** — подтверждение перед использованием
* 📞 **Контакты** — связь с менеджером

### Для администратора 
* 📊 **Статистика** — количество пользователей
* 📢 **Рассылка** — отправка сообщений всем пользователям (текст/фото/видео)
* 👥 **Список пользователей** — последние 10

## Quick Start

### 1. Local development

# Clone repository
git clone https://github.com/yourusername/telegram-shop-bot
cd telegram-shop-bot

# Virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

2. Environment variables

Create .env file:
env

BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db

3. Run bot
bash

python bot.py

API Endpoints

Бот использует Telegram Bot API. Основные команды:
Команда	Описание	Доступ
/start	Начало работы + согласие	👤
/catalog	Каталог товаров	👤
/cart	Корзина	👤
/payment	Реквизиты для оплаты	👤
/admin	Админ-панель	🔒
Callback Data

Префиксы callback-запросов от inline-кнопок:

    category_* — выбор категории

    item_*_* — просмотр товара

    add_*_* — добавить в корзину

    pay_#* — оплата заказа

    confirm_#* — подтверждение оплаты

    admin_* — админские действия

Database Schema
sql

users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    joined_date TEXT
)

Deployment (Railway)

    Push to GitHub

    railway.app → New Project → Deploy from GitHub

    Add environment variables:

        BOT_TOKEN

        DATABASE_URL (Railway PostgreSQL)

    Deploy 🚀

Commands History

    25c3f1a — add PostgreSQL, refactor admin broadcast, fix payment callback

    b8e7d2f — add terms acceptance, main menu keyboard

    a1b2c3d — initial commit: catalog, cart, payment

