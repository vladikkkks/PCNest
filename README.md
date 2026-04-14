# PC-NEST

## Швидкий старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Налаштування БД

За замовчуванням проєкт використовує PostgreSQL.

1. Створіть БД і користувача через скрипт:
   `psql -U postgres -f db/init_postgres.sql`
2. Заповніть `.env` значеннями `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
3. Виконайте міграції:
   `python manage.py migrate`

Якщо PostgreSQL недоступний локально, можна тимчасово перейти на SQLite:

```env
DB_ENGINE=sqlite
SQLITE_NAME=db.sqlite3
```

## Наповнення тестовими даними

Після міграцій виконайте:

```bash
python manage.py seed_demo_data
```

Створюються:
- користувач-адмін: `admin / admin12345`
- demo-користувач: `demo / demo12345`
- тестові компоненти та приклад збірки.

Також можна одразу запустити сайт з автозаповненням:

```bash
python run_site.py --sqlite --seed-demo
```

## Реальні фото компонентів

Щоб підтягнути справжні фото для демо-компонентів:

```bash
DB_ENGINE=sqlite python manage.py fetch_real_component_photos
```

Перезаписати вже наявні фото:

```bash
DB_ENGINE=sqlite python manage.py fetch_real_component_photos --force
```
