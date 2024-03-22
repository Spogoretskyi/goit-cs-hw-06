FROM python:3.11

ENV APP_HOME /app

COPY . .

WORKDIR $APP_HOME

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]