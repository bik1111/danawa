FROM python:3.9

WORKDIR /usr/src
RUN apt-get update
RUN pip install --upgrade pip

RUN apt-get update

COPY slack ./slack

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/slack

CMD ["python3", "slack.py"]