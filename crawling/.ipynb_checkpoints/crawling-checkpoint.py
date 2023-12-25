#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup


# # 차례
# ### 1. 크롤링을 통한 상품 정보 및 리뷰 수집
# ### 2. CSV 변환
# ### 3. 데이터 전처리 (한글만 filtering, 띄어쓰기 수정,
# ### 3. Embedding Vector
# ### 4. Cosine Similarity 구하기
# ### 5. chatGPT 연동

# # 1. 크롤링을 통한 상품 정보 및 리뷰 수집

import re
import os
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

data_list = []

def crawl_page(url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)

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
        time.sleep(5)  # Add a delay to allow the next page to load

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
        time.sleep(1)
        # 정규 표현식을 사용하여 한글만 남기기
        cleaned_reviews = [re.sub(r'[^가-힣\s]', '', review.get_text()) for review in reviews]

        # 리뷰를 해당 상품의 딕셔너리에 추가
        item['reviews'] = cleaned_reviews
        time.sleep(2)


# Initial URL
initial_url = "https://search.shopping.naver.com/search/category/100005307"

if __name__ == "__main__":
    crawl_page(initial_url)
    time.sleep(3)
    review_crawl()



# # 2. CSV 변환하기

# In[206]:


import csv

def save_to_csv(data_list, file_path='output.csv'):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())

        # CSV 파일 헤더 쓰기
        writer.writeheader()

        # 데이터 쓰기
        writer.writerows(data_list)

save_to_csv(data_list)


# In[207]:


import pandas as pd

# CSV 파일을 DataFrame으로 읽기
df = pd.read_csv('output.csv')

# DataFrame 확인
print(df)


# # 3. 데이터 전처리

# ### 3-1) 한글만 남기기

# In[210]:


import re

def extract_word(text):
    hangul = re.compile('[^가-힣]')
    result = hangul.sub(' ', text)
    return result

df['reviews'] = df['reviews'].apply(lambda x: extract_word(x))


# ### 3-2) 띄어쓰기 고치기
#
# ref : 한국어 전처리 패키지(Text Preprocessing Tools for Korean Text) - 딥 러닝을 이용한 자연어 처리 입문 (wikidocs.net)

# In[211]:


from pykospacing import Spacing

spacing = Spacing()

df['reviews'] = df['reviews'].apply(lambda x: spacing(x))


# # 3. Embeding Vector 추출하기

# In[212]:


from sentence_transformers import SentenceTransformer

# Initialize the SentenceTransformer model
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")
df['hf_embeddings'] = df['reviews'].apply(lambda x : embedder.encode(x))


# # 4. 코사인 유사도(Cosine Similarity) 구하기

# In[213]:
import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

def get_query_sim_top_k(query, model, df, top_k):
    # Encode the query
    query_encode = model.encode(query)

    # Compute cosine similarity
    cos_scores = util.pytorch_cos_sim(query_encode, df['hf_embeddings'])[0]

    # Get top k results
    top_results_idx = torch.topk(cos_scores, k=top_k).indices.cpu().numpy()
    top_results_df = df.iloc[top_results_idx][['product_name', 'product_link_url']]

    return top_results_df

get_query_sim_top_k("대학생들이 사용하기에 좋은 노트북", model, df, 5)






