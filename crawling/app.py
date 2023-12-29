from flask import Flask, jsonify
from crawling import crawl_product_info
from loading_data_dynamo import load_data_from_dynamo
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route('/health', methods=['GET'])
def health_check():
    # Add any additional checks if needed
    # For example, check if the database is accessible, external services are reachable, etc.

    # Return a JSON response indicating the server is healthy
    return jsonify(status='ok')

@app.route('/api/crawling', methods=['GET'])
def crawl_data():
    # Add any additional logic for crawling here
    crawl_product_info()

    # Return a response indicating the crawling is complete
    return jsonify(message='Crawling completed successfully')


@app.route('/api/load_data', methods=['GET'])
def load_data():
    # Add any additional logic for loading data here
    load_data_from_dynamo()

    # Return a response indicating the loading data is complete
    return jsonify(message='Loading data completed successfully')


@app.route('/api/recommend', methods=['GET'])
def recommend_laptop():
    # Add any additional logic for recommending here
    return jsonify(message='Recommendation completed successfully')





if __name__ == '__main__':
    logging.info("start server!")

    app.run(host='0.0.0.0', port=3000, debug=True)
