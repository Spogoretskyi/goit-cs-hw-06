FROM python:3.11

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]