FROM python:3.10.4-slim

COPY . .
RUN pip install -r requirements.txt

CMD [ "python", "-u", "./main.py" ]
