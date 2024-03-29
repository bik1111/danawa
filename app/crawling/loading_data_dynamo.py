import decimal
import time
import boto3
import csv
from decimal import Decimal
import json



def load_data_from_dynamo():

    # AWS 자격 증명 설정 및 DynamoDB 클라이언트 생성
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')  # 리전은 사용하는 AWS 리전으로 변경
    table_name = 'danawa'
    table = dynamodb.Table(table_name)

    # CSV 파일 읽기
    csv_file_path = 'output.csv'
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)


        # 각 행에 대한 작업 수행
        for i, row in enumerate(reader):
            try:
                laptop_id = i + 1
                product_name = row['product_name']
                product_price = int(row['product_price'].replace(',', ''))
                product_spec = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in row['product_spec'].split(",") if len(item.split(":")) == 2}
                product_link_url = row['product_link_url']
                reviews = row['reviews']
                hf_embeddings = json.loads(row['hf_embeddings'], parse_float=Decimal)

            except decimal.InvalidOperation as e:
                print(f"Error in row {i}: {e}")
                print(f"Row data: {row}")

            #print(hf_embeddings)
            table.put_item(
                Item={
                    'laptop_id': i + 1,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_spec': product_spec,
                    'product_link_url': product_link_url,
                    'reviews': reviews,
                    'hf_embeddings': hf_embeddings
                }
            )
            time.sleep(10)  # Proper indentation

        print(f"Successfully added laptop items to DynamoDB")

