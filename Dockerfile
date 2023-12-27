FROM --platform=linux/amd64  python:3.9
WORKDIR /app
RUN apt-get update

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Check chrome version
RUN google-chrome --version

# Install ChromeDriver.
RUN apt-get install wget
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /app/chrome


COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/crawling

CMD [ "python3", "healthCheck.py" ]