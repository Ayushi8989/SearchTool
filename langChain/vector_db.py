import os
from dotenv import load_dotenv
import numpy as np
import openai
import pandas as pd
import faiss
import ast
from sentence_transformers import SentenceTransformer
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document
)
from llama_index.vector_stores.faiss import FaissVectorStore

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('API_KEY')
print("OpenAI API Key Loaded:", bool(openai.api_key))

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = embedding_model.get_sentence_embedding_dimension()

# Initialize FAISS index
faiss_index = faiss.IndexFlatL2(embedding_dim)
print("FAISS index initialized successfully!")

# Load the dataset
courses_data = pd.read_csv('analytics_vidhya_courses.csv')

# Format curriculum column
def format_curriculum(curriculum):
    formatted = []
    for chapter in curriculum:
        chapter_title = chapter['chapter-title']
        lessons = ', '.join(chapter['lessons'])
        formatted.append(f"{chapter_title}: {lessons}")
    return '; '.join(formatted)

# Process curriculum into a combined string
courses_data['curriculum_str'] = courses_data['curriculum'].apply(lambda x: format_curriculum(ast.literal_eval(x)))
courses_data['combined_text'] = (
    courses_data['title'] + " " + courses_data['description'] + " " + courses_data['curriculum_str']
)

# Create vector store
vector_store = FaissVectorStore(faiss_index=faiss_index)

# Create documents and generate embeddings
documents = []
embeddings = []
for _, row in courses_data.iterrows():
    text = f"Title: {row['title']}\nDescription: {row['description']}\nCurriculum: {row['curriculum_str']}"
    embedding = embedding_model.encode(text)
    documents.append(Document(text=text, embedding=embedding))
    embeddings.append(embedding)

# Add embeddings to FAISS
faiss_index.add(np.array(embeddings))

# Initialize LlamaIndex with FAISS vector store
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# Persist index and FAISS vector store
index.storage_context.persist()
print("RAG system built and index saved successfully.")

# Create a mapping of DataFrame indices to embedding positions
index_mapping = list(courses_data.index)

# Querying the FAISS index using a natural language query
query = "LLM"
query_embedding = embedding_model.encode(query).reshape(1, -1)

# Search for top 5 relevant documents from FAISS
distances, indices = faiss_index.search(query_embedding, k=5)

# Print the top results
print("\nTop 5 Results from FAISS:")
for idx in indices[0]:
    # Map FAISS index back to DataFrame index
    actual_index = index_mapping[idx]
    print(f"Result: {courses_data.iloc[actual_index]['title']}")

