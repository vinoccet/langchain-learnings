# pip install langchain langchain-core langchian-openai langchain-google-genai

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv(override=True)
http_client=httpx.Client(verify=False)
llm=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
)

llm_openai=ChatOpenAI(
    model="gpt-4o-mini",
    http_client=http_client
)

llm_laguna=ChatOpenAI(
      model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  
)

response=llm.invoke("Say hi in single word")
response_laguna=llm_laguna.invoke("tell some fun fact about computers")

print(response.content)
print(response_laguna.content)
