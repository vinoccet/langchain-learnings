from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import httpx
import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import TypedDict

load_dotenv(override=True)
http_client=httpx.Client(verify=False)
llm_gemini=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
)

llm_openai=ChatOpenAI(
    model="gpt-4o-mini",
    http_client=http_client
)

# reponse= llm_openai.invoke("Tell me a joke")

# print(reponse.content)

class Joke(BaseModel):
    setup:str
    punchline:str

class Joke_typedict(TypedDict):
    setup:str
    punchline:str

obj=Joke_typedict({"sumup":"test setup","punchline":"test punch"})
print(obj)
print(type(obj))
structured_output_llm=llm_gemini.with_structured_output(Joke_typedict)
response=structured_output_llm.invoke("Tell me a Joke")
print(response)
print(type(response))

# obj=Joke(**{"setup":"some setup","punchline":"test punchline"})
# print(type(obj))
# print(obj)



# joke={"setup":"",
#       "punchline":""}
# def generate_content(joke):
#     return "test"