from openai import OpenAI
import fitz  # PyMuPDF
from pinecone import Pinecone, ServerlessSpec
import json
import requests
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


def get_question():
    while not pc.describe_index(index_name).status['ready']:
        print("Não consegui conectar no Pinecone")

    #Lendo o input e gerando seu embedding
    audio = "Bom dia, Osvaldo, tudo certo? Passando para a gente alinhar as coisas que ficaram pendentes para a gente fazer no domingo. Um cara com serviços que acabaram que a gente não conseguiu tocar durante semana, mas deixa eu explicar aqui para vocês algumas coisas que a gente tem que resolver logo, tá bom? Então, conhecendo pela linha 3, eu preciso que façam a alunificação dos rolamentos ali. Essa máquina ali, ela já está dando sinais de esgar, já tem um certo tempo. O pessoal reportou já barulho estranho, já nesse equipamento, então tem que botar o lubrificante correto, ele já está no estoque, que ele código lá o azul 6624, então já toma cuidado com isso, já faz essa lubrificação com essa máquina aí, e não pode esquecer de conferir a fichia técnica dele para colocar a quantidade certa, tal, outra vez deu problema. Então depois disso eu preciso também que vocês dê uma verificada no nível de óleo lá da desencapadora, lá da linha 12, É um equipamento que, do nada, dá uns picos de temperatura lá, o pessoal já reportou, já mandou para a gerência, foi uma merda isso. Então, revisar mesmo as medições, ver se está tudo certo lá com o nível de óleo dela, porque se saiu do óleo recometado, ela vai começar a esquentar e com o risco de parar aí, vai dar BO. e também queria que a gente precisa dar uma olhada lá no compressor 5 aquele lá bem da central né o filtro de A já passou do ponto ele tava pra ser trocado na última parada mas ele acabou ficando pra agora então tá bem crítico então tem que fazer substituição agora agora no domingo já não dá pra esperar o filtro de novo já pexei mandei o menino trazer lá do almoxarifado tá debaixo da bancada só vocês pegarem e trocar também, tá? E aproveita que você tá no compressor, aproveita e dá um polinho lá naquela bomba da bomba de circulação, aquela lá do canto, do canto direito, ela também tava, o pessoal falou que ela tá fazendo barulho, aproveita e dá uma olhadinha lá pra mim, tá? Basicamente isso, qualquer coisa aí você não me avisa, tá? Porque eu tô de folga, eu seguramente resolve. Valeu!"

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
    for i,chunk in enumerate(relevant_chunks):
        print(f"Relevant Chunk {i}: {chunk}")

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

    #print(completion.choices[0].message.content)

get_question()