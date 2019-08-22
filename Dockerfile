FROM python:alpine3.7
COPY ./jovem-aprendiz-bot /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python ./telegram.py
