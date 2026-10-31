import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
apikey = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
print("API KEY LOADED",bool(apikey))
print(model)
if not apikey:
    raise ValueError("openkey not set in environment variable")

client = OpenAI(api_key=apikey)
response = client.responses.create(model=model,input = "Explain Generative AI in 3 sentence")
print (response.output_text)

