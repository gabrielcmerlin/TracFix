from openai import OpenAI
import fitz  # PyMuPDF
from pinecone import Pinecone, ServerlessSpec
import json
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

#Abrindo o OpenAI 

client = OpenAI(api_key=openai_key)

#Abrindo o Pinecone
pc = Pinecone(api_key=pinecone_key)
index_name = "tractian"
index = pc.Index(index_name)

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding


def get_question(audio):
    while not pc.describe_index(index_name).status['ready']:
        print("Não consegui conectar no Pinecone")

    input = f"""Leia o seguinte texto: {audio}. Ignore opiniões e saudações e gere instruções para cada tarefa solicitada. 
    Cada instrução deve conter um passo a passo de como realizar e as ferramentas necessárias, junto de seus nomes e códigos. 
    Escreva uma lista de JSONs. Deve haver n JSONS, um para cada tarefa. Cada JSON deve conter um campo para cada ferramenta junto de seu código, 
    um campo para cada instrução e um título, que deve ser escrito apenas com letras minúsculas e sem espaços, como um nome de arquivo.
    Exemplo: 
    [
        {{
        'titulo': 'engraxar_rolamentos',
        ' passo_a_passo': '1. passo1, 2. passo2, n. passon',
        'ferramentas': '1. ferramenta1, 2. ferramenta2, n. ferramentan'
        }},

        {{
        'titulo': 'montar_cadeira',
        ' passo_a_passo': '1. passo1, 2. passo2, n. passon',
        'ferramentas': '1. ferramenta1, 2. ferramenta2, n. ferramentan
        }},
    ]

    Não escreva nada além do JSON.
    """
    input = f"""Leia o seguinte texto: {audio}. Ignore opiniões e saudações e gere instruções para cada tarefa solicitada. 
    Cada instrução deve conter um passo a passo de como realizar e as ferramentas necessárias, junto de seus nomes e códigos. 
    Escreva uma lista de JSONs. Deve haver n JSONS, um para cada tarefa. Cada JSON deve conter um campo para cada ferramenta junto de seu código, 
    um campo para cada instrução e um título, que deve ser escrito apenas com letras minúsculas e sem espaços, como um nome de arquivo.
    Exemplo: 
    [
        {{
        'titulo': 'engraxar_rolamentos',
        ' passo_a_passo': '1. passo1, 2. passo2, n. passon',
        'ferramentas': '1. ferramenta1, 2. ferramenta2, n. ferramentan'
        }},

        {{
        'titulo': 'montar_cadeira',
        ' passo_a_passo': '1. passo1, 2. passo2, n. passon',
        'ferramentas': '1. ferramenta1, 2. ferramenta2, n. ferramentan
        }},
    ]

    Não escreva nada além do JSON.
    """

    input_embedding = get_embedding(input)

    # Define how many matches to retrieve
    num_matches = 10

    # Query the index with the input embedding
    results = index.query(vector=input_embedding, top_k=num_matches, include_metadata=True)

    # Extract text of the relevant chunks
    relevant_chunks = [match['metadata']['text'] for match in results['matches']]

    context = "\n\n".join(relevant_chunks)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente muito solícito para operários de uma fábrica. Você responde perguntas com base em contextos fornecido previamente."},
            {
            "role": "user", 
            "content": f"Contexto:\n{context}\n\nPergunta: {input}"
        }
        ]
    )

    return completion.choices[0].message.content
