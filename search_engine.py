import logging
import numpy as np
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from models import Document, get_db
from cache import cache_set, cache_get
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import pickle


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_and_index_document(file_path):
    try:
        logging.info(f"Loading document from {file_path}")
        cached_index = cache_get(file_path)
        if cached_index:
            logging.info("Loaded index from cache.")
            return cached_index

        loader = PyPDFLoader(file_path)
        docs = loader.load()
        embeddings = OpenAIEmbeddings()
        index = FAISS.from_documents(docs, embeddings)

        db = next(get_db())
        for doc in docs:
            embedding = embeddings.embed_query(doc.page_content)
            document = Document(filename=file_path, content=doc.page_content, embedding=pickle.dumps(embedding))
            db.add(document)
        db.commit()

        cache_set(file_path, index)
        logging.info("Document indexed and cached successfully.")
        return index
    except Exception as e:
        logging.error(f"Error loading document: {str(e)}")
        return None


def perform_semantic_search(query, top_k=5, threshold=0.5):
    try:
        logging.info(f"Performing semantic search for query: {query}")
        embeddings = OpenAIEmbeddings()
        query_embedding = embeddings.embed_query(query)
        
        db = next(get_db())
        results = db.query(Document).all()
        
        logging.info(f"Total documents in database: {len(results)}")
        
        filtered_results = []
        for doc in results:
            if doc.embedding is None:
                logging.warning(f"Document with ID {doc.id} has None embedding")
                continue
            doc_embedding = pickle.loads(doc.embedding)
            similarity = cosine_similarity(query_embedding, doc_embedding)
            logging.debug(f"Document ID: {doc.id}, Similarity: {similarity}")
            if similarity >= threshold:
                filtered_results.append((doc, similarity))
        
        filtered_results.sort(key=lambda x: x[1], reverse=True)
        top_results = filtered_results[:top_k]
        
        logging.info(f"Search completed. Found {len(top_results)} relevant documents.")
        
        if not top_results:
            logging.warning("No results found. Consider lowering the threshold.")
            return {"debug_info": {
                "total_docs": len(results),
                "threshold": threshold,
                "max_similarity": max([sim for _, sim in filtered_results]) if filtered_results else None
            }}
        
        return [{"content": doc.content, "similarity": sim} for doc, sim in top_results]
    except Exception as e:
        logging.error(f"Error during semantic search: {str(e)}")
        return None

def question_answering(query):
    try:
        logging.info(f"Running question-answering for query: {query}")
        db = next(get_db())
        documents = db.query(Document).all()
        texts = [doc.content for doc in documents]
        embeddings = OpenAIEmbeddings()
        faiss_index = FAISS.from_texts(texts, embeddings)
        retriever = faiss_index.as_retriever()
        
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        result = chain({"query": query})
        
        logging.info("Answer generated successfully.")
        return result['result']
    except Exception as e:
        logging.error(f"Error during question answering: {str(e)}")
        return None

def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        logging.warning("Encountered None embedding")
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def check_database_integrity():
    db = next(get_db())
    docs_with_none_embeddings = db.query(Document).filter(Document.embedding.is_(None)).all()
    if docs_with_none_embeddings:
        logging.warning(f"Found {len(docs_with_none_embeddings)} documents with None embeddings")
        for doc in docs_with_none_embeddings:
            logging.warning(f"Document ID {doc.id} has None embedding")

def reindex_documents():
    db = next(get_db())
    docs_to_reindex = db.query(Document).filter(Document.embedding.is_(None)).all()
    embeddings = OpenAIEmbeddings()
    for doc in docs_to_reindex:
        try:
            doc.embedding = embeddings.embed_query(doc.content)
            db.commit()
            logging.info(f"Re-indexed document ID {doc.id}")
        except Exception as e:
            logging.error(f"Failed to re-index document ID {doc.id}: {str(e)}")




