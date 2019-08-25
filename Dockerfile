FROM python:alpine3.7
COPY ./jovem-aprendiz-bot/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
