import boto3
from decouple import config
import csv

# Set your AWS credentials
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')


def load_data_from_dynamo():
    # AWS 자격 증명 설정 및 DynamoDB 클라이언트 생성
    dynamodb = boto3.resource('dynamodb', region_name='your-region')  # 리전은 사용하는 AWS 리전으로 변경
    table_name = 'your-dynamodb-table-name'  # 사용하는 DynamoDB 테이블 이름으로 변경
    table = dynamodb.Table(table_name)

    # CSV 파일 읽기
    csv_file_path = 'output.csv'
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # 각 행에 대한 작업 수행
        for row in reader:
            product_name = row['product_name']
            product_price = row['product_price']
            product_spec = row['product_spec']
            product_link_url = row['product_link_url']
            reviews = eval(row['reviews'])  # 문자열을 리스트로 변환
            hf_embeddings = [float(value.replace('[', '').replace(']', '').strip()) for value in row['hf_embeddings'].split(',')]


            # DynamoDB에 데이터 삽입
            table.put_item(
                Item={
                    'ProductName': product_name,
                    'ProductPrice': product_price,
                    'ProductSpec': product_spec,
                    'ProductLinkURL': product_link_url,
                    'Reviews': reviews,
                    'HFEmbeddings': hf_embeddings
                }
            )


