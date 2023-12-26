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
RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip

RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /app/chrome

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "crawling.py" ]