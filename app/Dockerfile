FROM python:3.8

EXPOSE 8000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

#COPY . /app

CMD python app.py