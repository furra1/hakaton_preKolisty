1. Установка зависимостей
bash
pip install aiohttp dnspython requests
2. Запуск системы
bash
# Запуск сервера (в первом терминале)
python main.py

# Запуск агента (во втором терминале)  
python run_agent.py
3. Использование
Откройте в браузере: http://localhost:8000

📋 Полное руководство
Архитектура системы
text
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Frontend   │    │   Backend    │    │   Agents    │
│  (Browser)  │◄──►│  (aiohttp)   │◄──►│  (Python)   │
└─────────────┘    └──────────────┘    └─────────────┘
Структура проекта
app/ - Backend приложение (routes, handlers, services)

checks/ - Модули сетевых проверок (ip_checks.py)

static/ - Frontend файлы (HTML, JS)

agent_database.py - База данных агентов

main.py - Главный сервер

agent.py - Код агента

run_agent.py - Скрипт запуска агента

Шаг 1: Запуск сервера
bash
python main.py
✅ Сервер запустится на http://localhost:8000

Шаг 2: Запуск агента
bash
# Базовый запуск
python run_agent.py

# С кастомными параметрами
python run_agent.py --name "Москва-агент" --location "Москва" --server http://localhost:8000
Шаг 3: Использование веб-интерфейса
Главная страница (http://localhost:8000)

Введите хост (например: google.com)

Выберите типы проверок

Нажмите "Проверить"

История проверок (http://localhost:8000/history.html)

Просмотр всех выполненных проверок

Повтор проверок

Фильтрация по статусу

Статус агентов (http://localhost:8000/agents.html)

Мониторинг активности агентов

Статистика системы

🔧 Типы проверок
Ping - ICMP проверка доступности

HTTP/HTTPS - проверка веб-серверов

TCP Port - проверка TCP портов

DNS Lookup - DNS запросы

Traceroute - трассировка маршрута

📡 API Endpoints
Управление проверками
POST /api/check - создать проверку

GET /api/check/{id} - получить результаты

GET /api/history - история проверок

GET /api/stats - статистика

DELETE /api/check/{id} - удалить проверку

Управление агентами
GET /api/agents - список агентов

POST /api/agents - регистрация агента

POST /api/agents/heartbeat - обновление активности

GET /api/agent/tasks - получение задач

POST /api/agent/results - отправка результатов

🤖 Работа с агентами
Автоматическая регистрация
Агенты автоматически регистрируются при первом запуске:

Генерируется уникальный токен

Определяется локация и IP

Статус: awaiting_heartbeat → active

Ручная регистрация через API
bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мой агент",
    "location": "Москва",
    "ip": "192.168.1.100",
    "token": "секретный_токен"
  }'
Мониторинг агентов
active - агент онлайн

inactive - агент офлайн

awaiting_heartbeat - ожидание первого подключения

Агенты отправляют heartbeat каждые 30 секунд.
