import requests
from bs4 import BeautifulSoup
import re
import csv
import logging
import requests
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from sentence_transformers import SentenceTransformer
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


logging.basicConfig(level=logging.INFO)

data_list = []

url = "https://search.shopping.naver.com/search/category/100005307"


def crawl_page(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        logging.info("Crawling start!!")

        driver.implicitly_wait(3)
        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")

        for page_number in range(1, 7):  # 최대 10 페이지까지 크롤링
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            products = soup.select('div.product_item__MDtDF')

            for v in products:
                item_name = v.select_one('a.product_link__TrAac.linkAnchor').get('title')
                item_price = v.select_one('span.price_num__S2p_v em').text
                item_specs = v.select('a.product_detail__oWDMs.product_bar__dHjkA.linkAnchor')
                specs = ', '.join([item_spec.text for item_spec in item_specs])
                item_href = v.select_one('a.product_link__TrAac.linkAnchor').get('href')

                data_list.append({
                    "product_name": item_name,
                    "product_price": item_price,
                    "product_spec": specs,
                    "product_link_url": item_href,
                })

            if new_height == last_height:
                break

            # 다음 페이지 버튼 클릭
            next_page_selector = f"#content > div.style_content__xWg5l > div.pagination_pagination__fsf34 > div > a:nth-child({page_number + 1})"
            next_page_button = driver.find_element(By.CSS_SELECTOR, next_page_selector)
            next_page_button.click()
            time.sleep(2)
            last_height = new_height

    except Exception as e:
        logging.error(f"Crawling error: {str(e)}")
    finally:
        logging.info("Crawling end!!")
        logging.info(data_list[0])
        driver.quit()



def save_to_csv(data_list, file_path='output.csv'):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data_list.keys())

        # CSV 파일 헤더 쓰기
        writer.writeheader()

        # 데이터 쓰기
        writer.writerows(data_list)


# ### 3-1) 리뷰 수집 및 한글만 남기기
def review_crawl():

    for item in data_list:
        link_url = item['product_link_url']

        # 새로운 HTTP 요청을 보내서 리뷰 페이지를 크롤링
        response = requests.get(link_url)
        review_soup = BeautifulSoup(response.content, 'html.parser')
        # 리뷰 아이템 선택
        reviews = review_soup.select('p.reviewItems_text__XrSSf')
        time.sleep(1)
        # 정규 표현식을 사용하여 한글만 남기기
        cleaned_reviews = [re.sub(r'[^가-힣\s]', '', review.get_text()) for review in reviews]

        # 리뷰를 해당 상품의 딕셔너리에 추가
        item['reviews'] = cleaned_reviews
        time.sleep(2)






model = SentenceTransformer("jhgan/ko-sroberta-multitask")

def crawl_product_info():
    logging.info("start download chrome driver")
    # 크롤링 시작
    crawl_page(url)
    time.sleep(3)

    # 리뷰 크롤링
    logging.info('start review crawling')
    review_crawl()

    # CSV 파일로 저장
    save_to_csv(data_list)

    # CSV 파일 읽기
    logging.info('start reading csv')
    df = pd.read_csv('output.csv')

    # Convert the 'reviews' column from string representation to actual lists
    df['reviews'] = df['reviews'].apply(eval)

    # Embedding
    logging.info('start embedding')
    sentence_embeddings = model.encode(df['reviews'].apply(lambda x: " ".join(x)).to_numpy().tolist())

    logging.info('start saving csv with embeddings vector')
    # Convert the embeddings to a list and assign to 'hf_embeddings' column
    df['hf_embeddings'] = sentence_embeddings.tolist()

    # Save the DataFrame to a new CSV file
    df.to_csv('output.csv', index=False)

    #cosine similarity 구하기
    #print(get_query_sim_top_k("대학생들이 사용하기에 좋은 노트북", model, df, 5))

