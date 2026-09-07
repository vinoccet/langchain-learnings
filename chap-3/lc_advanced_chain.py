from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import httpx
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# pip install langchain-community dds
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

# first task will be to get the interesting topic

topic_template=ChatPromptTemplate.from_messages([
    ("system","You are expert reasearcher, generate result in single word"),
    ("user","Provide me an interesting topic based on {subject}")
])

str_output_parser=StrOutputParser()
topic_chain = topic_template | llm | str_output_parser

# print(topic_chain.invoke({"subject":"Science"}))

# second task will be to generate a content for posting in linkedin
content_template=ChatPromptTemplate.from_messages([
    ("system","You are a digital marketing expert, provide me a response in minimum 5 lines"),
    ("user","Generate me a good content from the given topic {topic} for my linkedin post")
])

content_chain = content_template | llm | str_output_parser 



def create_dict(text:str):
    return {"topic":text}

runnable_method=RunnableLambda(create_dict)

final_chain = topic_chain | runnable_method | content_chain

print(final_chain.invoke({"subject":"Artificial Intelligence"}))

# web_tool=DuckDuckGoSearchResults(num_results=2)

# print(web_tool.invoke("Tell the current was status between usa and iran"))