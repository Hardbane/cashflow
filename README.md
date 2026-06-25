# ДДС — веб-сервис для управления движением денежных средств

Готовое тестовое задание backend-разработчика: Django-приложение для учета операций ДДС с CRUD, фильтрами, справочниками, бизнес-валидацией зависимостей и REST API.

## Что реализовано

- Главная страница со списком операций ДДС.
- Фильтры по периоду дат, статусу, типу, категории и подкатегории.
- Создание, редактирование и удаление записей ДДС.
- Управление справочниками: статусы, типы операций, категории, подкатегории.
- Логические связи:
  - категория привязана к типу операции;
  - подкатегория привязана к категории;
  - в форме нельзя выбрать неподходящую категорию/подкатегорию;
  - серверная валидация дублирует клиентскую.
- Django Admin.
- Django REST Framework API:
  - `/api/records/`
  - `/api/statuses/`
  - `/api/types/`
  - `/api/categories/`
  - `/api/subcategories/`
- Dockerfile и docker-compose для быстрого деплоя на сервер.

## Технологии

- Python 3.12
- Django 5.x
- Django ORM
- Django REST Framework
- SQLite
- Bootstrap 5
- Gunicorn
- WhiteNoise
- Docker / Docker Compose

## Быстрый запуск локально через Docker

```bash
cp .env.example .env
# обязательно поменяйте SECRET_KEY и DJANGO_SUPERUSER_PASSWORD в .env

docker compose up --build -d
```

После запуска приложение будет доступно:

- UI: http://localhost:8000/
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

Логин/пароль админки берутся из `.env`:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=change-me-admin-password
```

## Деплой на удаленный хост

Ниже пример для Ubuntu/Debian-сервера.

### 1. Подключитесь к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### 2. Установите Docker и Compose plugin

```bash
apt update
apt install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3. Скопируйте проект на сервер

Вариант A — через GitHub:

```bash
git clone https://github.com/YOUR_USERNAME/cashflow-dds.git
cd cashflow-dds
```

Вариант B — через `scp` с локальной машины:

```bash
scp -r cashflow-dds root@YOUR_SERVER_IP:/opt/cashflow-dds
ssh root@YOUR_SERVER_IP
cd /opt/cashflow-dds
```

### 4. Настройте переменные окружения

```bash
cp .env.example .env
nano .env
```

Минимально поменяйте:

```env
DEBUG=0
SECRET_KEY=long-random-production-secret
ALLOWED_HOSTS=YOUR_SERVER_IP,your-domain.com
CSRF_TRUSTED_ORIGINS=http://YOUR_SERVER_IP:8000,https://your-domain.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=strong-admin-password
```

### 5. Запустите приложение

```bash
docker compose up --build -d
```

При старте контейнер автоматически выполнит:

```bash
python manage.py migrate --noinput
python manage.py seed_initial_data
python manage.py create_admin_from_env
python manage.py collectstatic --noinput
```

### 6. Проверьте работу

```bash
docker compose ps
docker compose logs -f web
```

Откройте в браузере:

```text
http://YOUR_SERVER_IP:8000/
http://YOUR_SERVER_IP:8000/admin/
http://YOUR_SERVER_IP:8000/api/
```

## Настройка базы данных

По умолчанию используется SQLite-файл:

```env
SQLITE_PATH=/app/data/db.sqlite3
```

В `docker-compose.yml` подключен volume:

```yaml
volumes:
  - ./data:/app/data
```

Это значит, что база сохраняется на хосте в папке `./data` и не пропадает при пересоздании контейнера.

## Полезные команды

Остановить сервис:

```bash
docker compose down
```

Перезапустить:

```bash
docker compose restart
```

Посмотреть логи:

```bash
docker compose logs -f web
```

Выполнить Django-команду внутри контейнера:

```bash
docker compose exec web python manage.py shell
```

Создать нового суперпользователя вручную:

```bash
docker compose exec web python manage.py createsuperuser
```

## Публикация в GitHub

```bash
git init
git add .
git commit -m "Initial cashflow DDS project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cashflow-dds.git
git push -u origin main
```

## Структура проекта

```text
cashflow-dds/
├── cashflow_project/        # настройки Django-проекта
├── ledger/                  # основное приложение ДДС
│   ├── models.py            # модели и бизнес-валидация
│   ├── forms.py             # формы UI
│   ├── views.py             # страницы и API viewsets
│   ├── serializers.py       # DRF-сериализаторы
│   ├── urls.py              # маршруты UI/API
│   ├── templates/ledger/    # Bootstrap-шаблоны
│   └── management/commands/ # seed и создание админа из env
├── docker/entrypoint.sh     # старт контейнера
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Примечания по безопасности

- Не коммитьте `.env` в GitHub.
- Задайте сложные `SECRET_KEY` и `DJANGO_SUPERUSER_PASSWORD` перед деплоем.
- Для продакшена с доменом лучше поставить Nginx/Traefik и HTTPS перед контейнером.
