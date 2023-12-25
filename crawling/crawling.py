import requests
from bs4 import BeautifulSoup
import re
import os
import re
import csv
import requests
#from pykospacing import Spacing
import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sentence_transformers import SentenceTransformer


def crawl_page(url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(4)
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")

    for page_number in range(1, 7):  # Crawl up to 10 pages
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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

        last_height = new_height

    driver.quit()

data_list = []

def review_crawl():
    for item in data_list:
        link_url = item['product_link_url']

        # 새로운 HTTP 요청을 보내서 리뷰 페이지를 크롤링
        response = requests.get(link_url)
        review_soup = BeautifulSoup(response.content, 'html.parser')
        # 리뷰 아이템 선택
        reviews = review_soup.select('p.reviewItems_text__XrSSf')
        # 정규 표현식을 사용하여 한글만 남기기
        cleaned_reviews = [re.sub(r'[^가-힣\s]', '', review.get_text()) for review in reviews]

        # 리뷰를 해당 상품의 딕셔너리에 추가
        item['reviews'] = cleaned_reviews


# Initial URL
initial_url = "https://search.shopping.naver.com/search/category/100005307"

def save_to_csv(data_list, file_path='output.csv'):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())

        # CSV 파일 헤더 쓰기
        writer.writeheader()

        # 데이터 쓰기
        writer.writerows(data_list)




# ### 3-1) 한글만 남기기
def extract_word(text):
    hangul = re.compile('[^가-힣]')
    result = hangul.sub(' ', text)
    return result



def get_query_sim_top_k(query, model, df, top_k):
    # Encode the query
    query_encode = model.encode(query)

    # Compute cosine similarity
    cos_scores = util.pytorch_cos_sim(query_encode, df['hf_embeddings'])[0]

    # Get top k results
    top_results_idx = torch.topk(cos_scores, k=top_k).indices.cpu().numpy()
    top_results_df = df.iloc[top_results_idx][['product_name', 'product_link_url']]

    return top_results_df



if __name__ == "__main__":
    crawl_page(initial_url)
    time.sleep(3)
    print("start review crawling")
    review_crawl()
    save_to_csv(data_list)

    df = pd.read_csv('output.csv')
    print("start extract word")
    df['reviews'] = df['reviews'].apply(lambda x: extract_word(x))

    #spacing = Spacing()
    #print("start spacing")
    #df['reviews'] = df['reviews'].apply(lambda x: spacing(x))


    # # 3. Embeding Vector 추출하기
    # Initialize the SentenceTransformer model
    embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")
    print("start embedding")
    df['hf_embeddings'] = df['reviews'].apply(lambda x : embedder.encode(x))

    model = SentenceTransformer("jhgan/ko-sroberta-multitask")

    get_query_sim_top_k("대학생들이 사용하기에 좋은 노트북", model, df, 5)



