import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение API ключа
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY не найден в .env файле")

# Инициализация клиента OpenAI
client = OpenAI(api_key=api_key)

def test_openai_connection():
    try:
        # Простой запрос к API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Привет! Как дела?"}]
        )
        
        # Получение ответа
        reply = response.choices[0].message.content
        logger.info(f"Ответ от OpenAI: {reply}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при подключении к OpenAI: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Тестирование подключения к OpenAI...")
    if test_openai_connection():
        logger.info("Подключение успешно!")
    else:
        logger.error("Ошибка подключения!") 