import torch
from sentence_transformers import SentenceTransformer, util
import ast
import boto3
import numpy as np
import logging
import torch.nn.functional as F

# DB 및 테이블 조회
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table_name = 'danawa'
table = dynamodb.Table(table_name)

# 데이터 조회
response = table.scan()
items = response['Items']
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

def get_query_sim_top_k(query, model, top_k, table):
    logging.info("start get_query_sim_top_k")
    query_embedding = model.encode(query)
    if query_embedding is None:
        # Handle the case where the encoding is None
        return None

    # Encode the query
    query_encode = torch.tensor(np.array([query_embedding]), dtype=torch.float)

    top_results_list = []

    # DynamoDB Query 사용
    response = table.scan(
        ProjectionExpression="laptop_id, product_name, product_price, product_spec, product_link_url, reviews, hf_embeddings"
    )

    items = response['Items']

    for item in items:
        laptop_id = item['laptop_id']
        product_name = item['product_name']
        product_price = item['product_price']
        product_spec = item['product_spec']
        product_link_url = item['product_link_url']
        reviews = item['reviews']
        hf_embeddings = np.array([float(value) for value in item['hf_embeddings']])
        hf_embeddings_tensor = torch.tensor(hf_embeddings, dtype=query_encode.dtype)
        cos_scores = util.pytorch_cos_sim(query_encode, hf_embeddings_tensor)

        top_results_list.append({'product_name' : product_name, 'product_link_url': product_link_url, 'cosine_similarity': cos_scores.item()})

    top_results_list.sort(key=lambda x: x['cosine_similarity'], reverse=True)
    top_k_results = [{'product_name': item['product_name'], 'product_link_url': item['product_link_url']} for item in top_results_list[:top_k]]

    return top_k_results

