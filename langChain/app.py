from dotenv import load_dotenv
import faiss
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document
)
from llama_index.vector_stores.faiss import FaissVectorStore
import os
import openai
import pandas as pd
from sentence_transformers import SentenceTransformer
import streamlit as st

# Load environment variables
load_dotenv()

openai.api_key = os.getenv('API_KEY')
print("OpenAI API Key Loaded:", bool(openai.api_key))

def run_model():
    # Initialize SentenceTransformer model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding_dim = embedding_model.get_sentence_embedding_dimension()

    # Initialize FAISS index
    faiss_index = faiss.IndexFlatL2(embedding_dim)
    print("FAISS index initialized successfully!")

    # Load the dataset
    courses_data = pd.read_csv('analytics_vidhya_courses.csv')

    # Combine text fields to create embeddings
    courses_data['combined_text'] = (
        courses_data['title'] + " " + courses_data['description'] + " " + courses_data['curriculum']
    )

    # Prepare the list of documents and their embeddings
    documents = []
    embeddings = []
    for _, row in courses_data.iterrows():
        text = f"Title: {row['title']}\nDescription: {row['description']}\nCurriculum: {row['curriculum']}"
        embedding = embedding_model.encode(text)
        documents.append(Document(text=text, embedding=embedding))
        embeddings.append(embedding)

    # Initialize FaissVectorStore with the FAISS index
    vector_store = FaissVectorStore(faiss_index=faiss_index)

    # Set up storage context for LlamaIndex
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Build the index with the documents
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    # Persist the storage context
    index.storage_context.persist()
    print("RAG system built and index saved successfully.")
    return index


def query_index(index, query_text):
    retriever = index.as_retriever()

    try:
        # Retrieve relevant nodes/documents for the input query
        nodes = retriever.retrieve(query_text)

        # Return the results
        results = []
        for node in nodes:
            results.append(f"Document: {node.text}")
        
        return "\n\n".join(results)

    except Exception as e:
        if "Rate limit" in str(e):
            st.error("Rate limit exceeded. Please wait and try again later.")
        else:
            st.error(f"An error occurred: {e}")
        return None


# Main function to run the entire flow
def main():
    st.title("Course Search")

    # Run model and build index
    index = run_model()

    # Input query text
    query_text = st.text_input("Enter your query:")

    if query_text:
        results = query_index(index, query_text)
        if results:
            st.subheader("Results:")
            st.text(results)
        else:
            st.warning("No results found.")
    else:
        st.warning("Please enter a query to search.")

if __name__ == "__main__":
    main()


