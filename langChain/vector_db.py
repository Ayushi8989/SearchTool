from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
import pandas as pd
import openai
import os

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv('API_KEY')

# Initialize the embedding model
Settings.embed_model = OpenAIEmbedding()

# Load and preprocess the dataset
df = pd.read_csv('analytics_vidhya_courses.csv')

def format_curriculum(curriculum):
    formatted = []
    for chapter in curriculum:
        chapter_title = chapter['chapter-title'] 
        lessons = ', '.join(chapter['lessons'])  
        formatted.append(f"{chapter_title}: {lessons}")
    return '; '.join(formatted)

# Create a new column for formatted curriculum strings
df['curriculum_str'] = df['curriculum'].apply(lambda x: format_curriculum(eval(x)))  

df['combined_text'] = df['title'] + " " + df['description'] + " " + df['curriculum_str']

documents = [Document(text=row['combined_text']) for _, row in df.iterrows()]

# Create a Vector Store Index from documents
index = VectorStoreIndex.from_documents(documents)

# Save the index to disk
index.save_to_disk("course_index.json")
print("Index created and saved successfully!")


