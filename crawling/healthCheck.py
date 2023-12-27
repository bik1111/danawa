from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    # Add any additional checks if needed
    # For example, check if the database is accessible, external services are reachable, etc.

    # Return a JSON response indicating the server is healthy
    return jsonify(status='ok')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
