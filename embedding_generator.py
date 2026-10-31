import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def generate_embeddings(chunks):
    texts =[chunk["text"]
            for chunk in chunks]
     
    response = client.embeddings.create(model="text-embedding-3-small",input = texts)
    embeddings = [item.embedding
                  for item in response.data ]
    return embeddings