# 🛠️ Dev Notes – DataPulse Backend

This file contains best practices, tips, and useful commands for developing with Django + Docker in this project.

---

## 🚀 Useful Commands

### Start the environment with Docker

```bash
docker compose up --build
```

### Access the Django application terminal

```bash
docker compose exec web bash
```

### Create migrations (whenever a model changes)

```bash
docker compose exec web python manage.py makemigrations
```

### Apply migrations to the database

```bash
docker compose exec web python manage.py migrate
```

### Create a superuser (admin)

```bash
docker compose exec web python manage.py createsuperuser
```

## 📌 Best practices and gotchas

1. Always create migrations before migrating
   If you create a new model (like User) and try to run migrate directly without makemigrations, Django won't understand that it needs to create that table, and this will cause "table does not exist" errors

👉 Always run:

```bash
docker compose exec web python manage.py makemigrations
```

2. Correct order when creating custom user model
   If you're using AUTH_USER_MODEL, you need to register the model before running any migration.
   Otherwise, the admin app will try to use Django's default model.

3. Resetting the database (in dev)
   If something goes very wrong with migrations:

```bash
docker compose down -v       # deletes containers and database
rm -rf backend/*/migrations  # deletes all migrations (except __init__.py)
```

Then, recreate:

```bash
docker compose up --build
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

## ✅ Checklist for creating a new Django app

1. docker compose exec web python manage.py startapp app_name

2. Add the app to INSTALLED_APPS

3. Create models, serializers, views and routes

4. Run makemigrations and migrate

## Running tests with Docker

### Basic test commands (with unbuffered output to see test group messages):

```bash
# Run all tests with visible group messages
docker-compose exec web env PYTHONUNBUFFERED=1 python manage.py test --settings=datapulse.test_settings -v 2

# Run specific test groups
docker-compose exec web env PYTHONUNBUFFERED=1 python manage.py test users.tests --settings=datapulse.test_settings -v 2

# Run JWT token tests only
docker-compose exec web env PYTHONUNBUFFERED=1 python manage.py test tests.test_token_api --settings=datapulse.test_settings -v 2
```

### Run specific test classes or methods:

```bash
# Run only User Model tests
docker-compose exec web env PYTHONUNBUFFERED=1 python manage.py test users.tests.UserModelTestCase --settings=datapulse.test_settings -v 2

# Run a single specific test
docker-compose exec web env PYTHONUNBUFFERED=1 python manage.py test users.tests.UserModelTestCase.test_user_string_representation --settings=datapulse.test_settings -v 2
```

### Quick test commands (without group messages):

```bash
docker-compose run --rm test
```

**Note:** Use `env PYTHONUNBUFFERED=1` and `-v 2` flags to see the colorful test group messages with emojis!
