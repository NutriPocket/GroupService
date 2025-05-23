FROM python:3.13-alpine

RUN apk add --no-cache tcl-dev tk-dev

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

COPY /src /code/src

CMD ["python3", "src/main.py"]