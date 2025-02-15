FROM python:3.10-alpine

WORKDIR /app/HydroponicSystem

COPY requirements.txt /app/HydroponicSystem/

RUN apk add --virtual .build-deps --no-cache postgresql-dev python3-dev musl-dev && \
        pip install --no-cache-dir -r requirements.txt 

COPY . /app/HydroponicSystem/

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]