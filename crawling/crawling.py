import requests
from bs4 import BeautifulSoup
import re
import csv
import requests
import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import ast
import time
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sentence_transformers import SentenceTransformer

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')               # headless
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(executable_path = "/app/chrome/chromedriver" , chrome_options=chrome_options)


data_list = []

def crawl_page(url):

    driver.implicitly_wait(3)
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")

    for page_number in range(1, 7):  # Crawl up to 10 pages
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

        # Click the next page button
        next_page_selector = f"#content > div.style_content__xWg5l > div.pagination_pagination__fsf34 > div > a:nth-child({page_number + 1})"
        next_page_button = driver.find_element(By.CSS_SELECTOR, next_page_selector)
        next_page_button.click()
        time.sleep(2)
        last_height = new_height

    driver.quit()


def review_crawl():
    for item in data_list:
        link_url = item['product_link_url']

        # 새로운 HTTP 요청을 보내서 리뷰 페이지를 크롤링
        response = requests.get(link_url)
        review_soup = BeautifulSoup(response.content, 'html.parser')
        # 리뷰 아이템 선택
        reviews = review_soup.select('p.reviewItems_text__XrSSf')
        time.sleep(2)

        # 리뷰를 해당 상품의 딕셔너리에 추가
        item['reviews'] = reviews
        time.sleep(1)


# Initial URL

def save_to_csv(data_list, file_path='output.csv'):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())

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

# TOP 5 추천 상품
def get_query_sim_top_k(query, model, df, top_k):
    # Encode the query
    query_encode = model.encode(query)

    # Convert string representations of lists to actual lists
    df['hf_embeddings'] = df['hf_embeddings'].apply(ast.literal_eval)

    # Compute cosine similarity
    cos_scores = util.pytorch_cos_sim(query_encode, torch.tensor(df['hf_embeddings'].tolist()))[0]

    # Get top k results
    top_results_idx = torch.topk(cos_scores, k=top_k).indices.cpu().numpy()
    top_results_df = df.iloc[top_results_idx][['product_name', 'product_link_url']]

    return top_results_df



initial_url = "https://search.shopping.naver.com/search/category/100005307"
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

def main():
    print("crawling start")
    # 크롤링 시작
    crawl_page(initial_url)
    time.sleep(3)

    # 리뷰 크롤링
    logging.infoing('start review crawling')
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

if __name__ == "__main__":
    main()




