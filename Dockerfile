FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app/

# Copy and set entrypoint
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "scrapy.wsgi:application", "--bind", "0.0.0.0:8000"]
