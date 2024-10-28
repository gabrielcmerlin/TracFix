from openai import OpenAI
import fitz  # PyMuPDF
from pinecone import Pinecone, ServerlessSpec
import json
import requests
import os
from dotenv import load_dotenv

#------------------------------------------LENDO PDF E TRANSFORMANDO EM CHUNKS DE TEXTO----------------------------------#

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

def chunk_text(text, max_words=150):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

pdf_path = "./codigos.pdf"
file_content = extract_text_from_pdf(pdf_path)
print(pdf_path.split("./")[1])

chunks = chunk_text(file_content)
print(f"Created {len(chunks)} chunks.")
#print("Sample Chunk:", chunks[0])

#-------------------------------------------------GERANDO EMBEDDINGS E UPANDO NO PINECONE--------------------------------------------------#

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

client = OpenAI(api_key=openai_key)
pc = Pinecone(api_key=pinecone_key)

#Nome do index no Pinecone
index_name = "tractian"

while not pc.describe_index(index_name).status['ready']:
    print("Não consegui conectar no Pinecone")

dimension = 1536  # For "text-embedding-ada-002" model

# Connect to the index
index = pc.Index(index_name)

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding


# Iterate through each chunk to create and upload embeddings
for i, chunk in enumerate(chunks):
    # Create embedding for the chunk
    

    embedding = get_embedding(chunk)

    print(f"{pdf_path.split("./")[1]}-{i}")

    # Upload chunk with a unique ID (e.g., using "chunk-<index>" as the ID)
    index.upsert([(f"{pdf_path.split("./")[1]}-{i}", embedding, {"text": chunk})])
