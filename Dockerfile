FROM python:3.9.5-slim

COPY . .
RUN pip install -r requirements.txt

CMD [ "python", "-u", "./main.py" ]
