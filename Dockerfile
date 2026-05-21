FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install flask mysql-connector-python bcrypt

EXPOSE 5000

CMD ["python", "app.py"]