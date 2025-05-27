# Telegram Scheduler Bot 🤖📅

## 🇷🇺 Русское описание

### Описание
Бот для Telegram, позволяющий планировать отложенные публикации в каналах с настраиваемыми интервалами времени. Идеальное решение для администраторов каналов, которые хотят автоматизировать публикацию контента.

### Возможности
- ✅ Поддержка множества каналов с индивидуальными интервалами публикации
- ✅ Публикация различных типов контента (текст, фото, видео, GIF, документы)
- ✅ Поддержка медиа-групп (альбомы)
- ✅ Удобное меню управления каналами и постами
- ✅ Просмотр и удаление запланированных публикаций
- ✅ Безопасность: доступ только для администраторов
- ✅ Нет ограничений на количество отложенных публикаций

### Требования
- Python 3.7 или выше
- Библиотеки из файла `requirements.txt`

### Установка и запуск
1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/telegram-scheduler-bot.git
cd telegram-scheduler-bot
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории проекта:
```
BOT_TOKEN=ваш_токен_бота
ADMIN_IDS=id1,id2,id3
```

4. Запустите бота:
```bash
python main.py
```

### Использование
1. Отправьте команду `/start` боту
2. Добавьте каналы с нужными интервалами публикации
3. Выберите канал и отправьте боту контент для публикации
4. Бот автоматически будет публиковать контент в указанные каналы с заданным интервалом

## 🇬🇧 English Description

### Description
A Telegram bot for scheduling delayed posts to channels with customizable time intervals. The perfect solution for channel administrators who want to automate content publishing.

### Features
- ✅ Support for multiple channels with individual publication intervals
- ✅ Publishing various types of content (text, photos, videos, GIFs, documents)
- ✅ Media group support (albums)
- ✅ Convenient menu for managing channels and posts
- ✅ View and delete scheduled publications
- ✅ Security: admin-only access
- ✅ No limits on the number of scheduled posts

### Requirements
- Python 3.7 or higher
- Libraries from the `requirements.txt` file

### Installation and Launch
1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-scheduler-bot.git
cd telegram-scheduler-bot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate  # for Windows
source venv/bin/activate  # for Linux/Mac
pip install -r requirements.txt
```

3. Create an `.env` file in the project root directory:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=id1,id2,id3
```

4. Start the bot:
```bash
python main.py
```

### Usage
1. Send the `/start` command to the bot
2. Add channels with the desired publication intervals
3. Select a channel and send content to the bot for publication
4. The bot will automatically publish content to the specified channels at the set intervals

## 📝 Структура проекта / Project Structure
```
telegram-scheduler-bot/
├── main.py         # Entry point
├── handlers.py     # Command and message handlers
├── scheduler.py    # Post scheduler
├── config.py       # Configuration and channel management
├── db.py           # Database operations
├── requirements.txt
└── .env            # Environment variables (not in repository)
```

## 📜 Лицензия / License
MIT 