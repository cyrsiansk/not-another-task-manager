# 📌 Task Manager API

**Task Manager API** — современное RESTful API для управления задачами с аутентификацией пользователей.  
Построено на **FastAPI** и использует **PostgreSQL**. Этот README — улучшенная, стильная и более читабельная версия исходного файла. fileciteturn0file0

---

## ✨ Что внутри
- 🔐 JWT-аутентификация
- ✅ CRUD для задач
- 🗂 Фильтрация задач по статусу
- 🔒 Оптимистичная блокировка для предотвращения конфликтов изменений
- 📊 Swagger / ReDoc для автоматической документации
- 🐳 Docker + docker-compose
- 📝 Миграции через Alembic
- 🧪 Unit- и acceptance-тесты (pytest, Gauge)
- 🔎 Линтинг и автоформатирование (Black, Ruff)

---

## 🧩 Быстрый старт

### Запуск (рекомендуемый — Docker Compose)
```bash
git clone https://github.com/cyrsiansk/not-another-task-manager.git
cd task-manager
docker-compose -f docker/docker-compose.yml up --build
```
После сборки приложение будет доступно: `http://localhost:8000`

### Запуск локально (без Docker)
```bash
python -m venv .venv
source .venv/bin/activate   # или .venv\Scripts\activate на Windows
pip install -r requirements.txt

# Настройте .env
# DATABASE_URL=postgresql+psycopg2://app:secret@localhost:5432/app_db
# SECRET_KEY=your-secret-key

alembic upgrade head
uvicorn app.main:app --reload
```

---

## 📚 Документация API
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

---

## 🔌 Основные эндпоинты

### Аутентификация
- `POST /api/v1/auth/register` — регистрация
- `POST /api/v1/auth/token` — получение JWT (логин)

### Работа с задачами (требуется авторизация)
- `GET /api/v1/tasks` — список задач (поддерживает фильтрацию)
- `POST /api/v1/tasks` — создать задачу
- `GET /api/v1/tasks/{id}` — получить задачу
- `PATCH /api/v1/tasks/{id}` — обновить задачу (поддерживает частичное обновление)
- `DELETE /api/v1/tasks/{id}` — удалить задачу

### Системные
- `GET /health` — health-check приложения

---

## 🧭 Конфигурация (важные переменные)
| Переменная | Описание | Пример / Значение по умолчанию |
|---|---:|---|
| `DATABASE_URL` | URL подключения к БД | `postgresql+psycopg2://app:secret@localhost:5432/app_db` |
| `SECRET_KEY` | Секрет для подписи JWT | `change-me` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (мин) | `60` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

---

## 🧪 Тесты
**Unit (pytest):**
```bash
pytest -v
```
**Acceptance (Gauge):**
```bash
gauge run specs
```
**CI (примерная последовательность):**
```bash
pip install -r requirements.txt
black --check .
ruff check .
pytest -v
gauge run specs
```

---

## 🗂 Структура проекта (кратко)
```
app/
├── api/v1/        # Эндпоинты
├── core/          # Конфиги, безопасность
├── crud/          # Операции с БД
├── db/            # Сессии и миграции
├── models/        # SQLAlchemy модели
├── schemas/       # Pydantic схемы
└── main.py        # Точка входа
docker/
specs/             # Gauge спецификации
step_impl/         # Gauge steps implementation
tests/             # Unit тесты
```

---

## 🛡️ Безопасность
- Хранение паролей: bcrypt
- JWT с коротким TTL
- Валидация входных данных через Pydantic
- Использование ORM для защиты от SQL-инъекций
- Оптимистичная блокировка для предотвращения race condition

---

## 🧰 Инструменты разработки
- Black, Ruff — форматирование и линтинг
- pre-commit — хуки
- GitHub Actions — CI/CD

---