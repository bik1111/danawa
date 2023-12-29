
import config
import re
from sentence_transformers import SentenceTransformer, util
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from server.response import get_query_sim_top_k  # Adjusted import statement
import random
import boto3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


app = App(token=config.bot_token)
slack_client = WebClient(token=config.bot_token)

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table_name = 'danawa'
table = dynamodb.Table(table_name)


@app.message()
def recommend_laptop(ack, body, payload, say):

    text = body.get('event', {}).get('text')
    say('안녕하세요 다나와 챗봇이 추천 로직을 돌리고 있으니 잠시만 기다려주세요! 💜🙏')

    recommend_products = get_query_sim_top_k(text, model, 3, table)
    print(recommend_products)

    for product in recommend_products:
        product_title = product['product_name']
        product_link_url = product['product_link_url']

        message = {
            "blocks": [
                {
                    "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*품목명:* {product_title}\n*자세히보기:*<{product_link_url}|링크>"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]
            }

        say(message)


if __name__ == '__main__':
    SocketModeHandler(app, config.app_token).start()

