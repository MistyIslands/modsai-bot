import os
import sys
import zulip
import logging
from logging.handlers import RotatingFileHandler
from openai import OpenAI
from openai import RateLimitError, APIError
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Создаем директорию для логов, если её нет
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
log_file = os.path.join(log_dir, "bot.log")
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
console_handler = logging.StreamHandler(sys.stdout)

# Формат логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Получение API ключа
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY не найден в .env файле")

# Инициализация клиентов
client = zulip.Client(config_file=".zuliprc")
openai_client = OpenAI(api_key=api_key)

def handle_message(message):
    # Проверяем, не является ли сообщение от самого бота
    if message["sender_email"] == "modsmechanic-bot@stage-chat.modsnation.com":
        logger.info("Пропускаем собственное сообщение")
        return

    try:
        user_msg = message["content"]
        user_id = message["sender_id"]
        
        # Игнорируем сообщения от пользователя с ID 35
        if user_id == 35:
            logger.info(f"Игнорируем сообщение от пользователя {user_id}")
            return
            
        logger.info(f"Получено сообщение от пользователя {user_id}: {user_msg}")
        
        # Запрос к OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )
        bot_reply = response.choices[0].message.content
        logger.info(f"Ответ от OpenAI: {bot_reply}")
        
    except RateLimitError as e:
        logger.error(f"Ошибка превышения квоты: {str(e)}")
        bot_reply = "Извините, в данный момент превышен лимит запросов к API. Пожалуйста, попробуйте позже."
    except APIError as e:
        logger.error(f"Ошибка API: {str(e)}")
        bot_reply = f"Произошла ошибка при обработке запроса: {str(e)}"
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}")
        bot_reply = f"Произошла непредвиденная ошибка: {str(e)}"
    
    try:
        client.send_message({
            "type": "stream",
            "to": message["display_recipient"],
            "subject": message["subject"],
            "content": bot_reply
        })
        logger.info("Сообщение успешно отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {str(e)}")

if __name__ == "__main__":
    logger.info("Бот запущен")
    # Подписываемся на все новые сообщения
    for event in client.call_on_each_message(lambda msg: handle_message(msg)):
        pass
