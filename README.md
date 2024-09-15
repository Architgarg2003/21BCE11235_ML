# Document Retrieval and Question Answering System

## Overview
This project implements a document retrieval and question-answering system using Flask, SQLite, FAISS, and OpenAI. The system allows users to upload PDF documents, which are then indexed for efficient retrieval. Users can perform semantic searches and ask questions about the content of the uploaded documents.

## Project Structure
- `app.py`: Main Flask application handling file uploads, search, and question-answering requests.
- `search_engine.py`: Core logic for document indexing, semantic search, and question answering.
- `databse.py`: SQLite database schema and session management.
- `models.py`: SQLAlchemy ORM models for the database.
- `cache.py`: Redis-based caching for document embeddings.
- `background_scraper.py`: Background task for scraping and indexing news articles.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/21BCE11235_ML.git
   cd 21BCE11235_ML


2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory with the following content:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

4. **Initialize the database:**
   ```bash
   python database.py
   ```

5. **Setup Radis**
   ```bash
   brew install redis
   ```

   ```bash
   brew services start redis
   ```

   ```bash
   redis-server
   ```

## Usage

1. **Run the Flask application:**

   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5001`.

2. **Upload a document:**
   Use `curl` to upload a PDF document:

   ```bash
   curl  -H "User-ID:USER_ID" -F "file=@/path/to/your/document.pdf" http://127.0.0.1:5001/upload
   ```

3. **Perform a search:**
   To perform a semantic search:

   ```bash
   curl  -H "User-ID:USER_ID"  "http://127.0.0.1:5001/search?text=your_query&top_k=5&mode=search"
   ```

4. **Ask a question:**
   To ask a question about the document:
   ```bash
   curl  -H "User-ID:USER_ID" "http://127.0.0.1:5001/search?text=your_question&mode=qa"
   ```

## Docker Setup

To build and run the application using Docker:

1. **Build the Docker image:**

   ```bash
   docker build -t document_retrieval_app .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -p 5000:5000 document_retrieval_app
   ```

## Debugging

Ensure that:

- Redis server is running and accessible.
- The `.env` file contains valid environment variables.
- # Document paths and queries are correctly formatted.

# 21BCE11235_ML

