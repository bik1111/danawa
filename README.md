## 🗣 자연어 기반 제품 추천 시스템 - Danawa(다나와)



<p align="center">
  <img src="https://github.com/bik1111/danawa/assets/76617139/e71b51cf-ee16-4486-b223-9669356d1081" alt="Danawa GIF">
</p>


<br>

## 🚀 Motivation of Project
나이가 많으신 혹은 E-commerce 상에서 상품 구매 과정에 대해 어려움을 느끼시는 분들에게 해당 과정에 대한 노고를 줄이고 직관적인 구매 경험을 제공하고자 하였습니다.

<br>

## 🛠 Skills

#### Language
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
#### Infra
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
#### Environment (CI/CD)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<br>


## 🌐 Development Architrecture (Data ETL Side)
![zzzzz1111](https://github.com/bik1111/danawa/assets/76617139/de7f0d78-4778-4371-a35e-493847d8eca3)



## 🌐 Service Architrecture
![ggggggggg](https://github.com/bik1111/danawa/assets/76617139/d18f9491-5bf5-4e4d-81d4-965c96a5b1ff)

<br>

## 💡 Sentence-transformers model 

- https://huggingface.co/jhgan/ko-sroberta-multitask
- https://github.com/jhgan00/ko-sentence-transformers

<br>

## ⛓ Data ETL & Response to user's query Process

1. ChromeDriver 및 Selenium, BeautifulSoup을 통한 네이버 쇼핑몰 내 상품의 상품명/가격/스펙/URL 크롤링
2. URL을 순회하며 해당 상품에 등록된 리뷰(Review) 크롤링
3. 수집된 데이터들을 CSV 형태로의 변환 및 저장
4. Sentence Transformer 모델을 사용하여 리뷰 Column Embedding 수행
5. Embedding 완료된 최종 데이터를 DynamoDB에 적재
6. 유저 요청 시, DB 스캔 후 Embedding Vector를 바탕으로 Cos-Similarity 계산
7. 유사도 기반 상위 K개 제품 반환




