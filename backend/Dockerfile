FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY backend/ /app/

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_superuser_if_none && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
