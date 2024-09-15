from flask import Flask, request, jsonify
from search_engine import perform_semantic_search, question_answering, load_and_index_document
from background_scraper import start_background_scraper
from models import User, get_db
from functools import wraps
import time
import os


app = Flask(__name__)

# Start background scraper
start_background_scraper()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({"error": "User-ID header is required"}), 400

        db = next(get_db())
        user = db.query(User).get(user_id)
        if not user:
            user = User(id=user_id, request_count=0)
            db.add(user)

        if user.request_count >= 5:
            return jsonify({"error": "Rate limit exceeded"}), 429

        user.request_count += 1
        db.commit()

        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return jsonify(message="Welcome to the Document Retrieval API")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is running"}), 200

@app.route('/upload', methods=['POST'])
@rate_limit
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        os.makedirs('uploads', exist_ok=True)
        filepath = f"./uploads/{file.filename}"
        try:
            file.save(filepath)
            load_and_index_document(filepath)
            return jsonify({"message": f"File uploaded and indexed successfully at {filepath}"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route('/search', methods=['GET'])
@rate_limit
def search():
    start_time = time.time()
    query = request.args.get('text')
    top_k = int(request.args.get('top_k', 5))
    threshold = float(request.args.get('threshold', 0.5))
    mode = request.args.get('mode', 'search')

    if not query:
        return jsonify({"error": "Query text is missing"}), 400

    try:
        if mode == 'search':
            results = perform_semantic_search(query, top_k, threshold)
        elif mode == 'qa':
            results = question_answering(query)
        else:
            return jsonify({"error": "Invalid mode"}), 400

        end_time = time.time()
        inference_time = end_time - start_time
        app.logger.info(f"Inference time: {inference_time:.2f} seconds")

        return jsonify({"results": results, "inference_time": inference_time}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to perform {mode}: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)