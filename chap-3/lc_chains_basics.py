# propmt | llm_connection | output
# .invoke

from dotenv import load_dotenv
import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

template="What is the capital of {country}"
prompt_template=PromptTemplate.from_template(template)



output_parser=StrOutputParser()

chain = prompt_template | llm | output_parser

print(chain.invoke({"country":"China"}))