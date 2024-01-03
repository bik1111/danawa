FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /usr/src
RUN apt-get update
RUN pip install --upgrade pip

RUN apt-get update
RUN apt-get install wget -y
RUN apt-get install -yqq unzip

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver.
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/src/chrome

COPY app ./app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

WORKDIR /usr/src/app

CMD ["python3", "main.py"]
