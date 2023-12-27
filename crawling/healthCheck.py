from flask import Flask, jsonify
from crawling import main
from threading import Thread

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    # Add any additional checks if needed
    # For example, check if the database is accessible, external services are reachable, etc.

    # Return a JSON response indicating the server is healthy
    return jsonify(status='ok')

def run_main():
    main()

if __name__ == '__main__':
    main_thread = Thread(target=run_main)
    main_thread.start()

    app.run(host='0.0.0.0', port=3000)
