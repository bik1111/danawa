# x86-64 Architecture
FROM --platform=linux/amd64 python:3.9

WORKDIR /app

RUN apt-get update
RUN apt-get install wget
RUN apt-get install -yqq unzip

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver.
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /app/chrome

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/crawling

EXPOSE 3000

CMD [ "python3", "app.py" ]