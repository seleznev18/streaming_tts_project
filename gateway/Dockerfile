FROM python:3.11-slim

WORKDIR /app

COPY ./app /app/app
COPY ./requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${GATEWAY_PORT}

CMD ["python", "-m", "app.main"]
