FROM python:3.11.2-alpine3.17

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD main.py /

CMD [ "python", "./main.py" ]
