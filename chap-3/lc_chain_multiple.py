from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import httpx
import os
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain.tools import tool
from langchain.agents import create_agent
from pydantic import BaseModel,Field
from typing import TypedDict

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
    model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client,
)


class User(BaseModel):
    name:str = Field(con)
    age:int

obj=User(**{"name":"","age":10})
print(obj)

structuredoutput=llm.with_structured_output(User)
print(structuredoutput.in)
# web_search=DuckDuckGoSearchResults()


# wikipedia = WikipediaAPIWrapper()
# wikipedia_tool=WikipediaQueryRun(api_wrapper=wikipedia)

# @tool
# def calculator(a,b):
#     """ returns the addition of 2 given numbers"""
#     return a+b

# toolk_kit=[web_search,wikipedia_tool,calculator]

# agent=create_agent(
#     model=llm,
#     tools=toolk_kit
# )
# print(agent.invoke({
#     "messages":[("user","what is the sum of 10 and 20?")]
# }))

# messages=ChatPromptTemplate.from_messages([
#     ("system","you are inteligent agent exposed with websearch, addition funtions"),
#     ("user","what is the sum of {number1} and {number2}")
# ]
# )
# m=messages.format_messages(number1=10,number2=25)
# events=agent.stream(
#  {    "messages":[("user","current weather in coimbatore?")]
# },
# stream_mode="values"
# )

# for event in events:
#     print(event["messages"][-1])
# social_media_template=ChatPromptTemplate.from_messages([
#     SystemMessage(content="you are a expert market reasearcher, looking for trending content"),
#     HumanMessagePromptTemplate.from_template("provide me a hot topic in {industry} industry to post in social media")
# ])

# def dictionary_creator(text:str):
#     return {"industry":text}

# runnable_dict_industry=RunnableLambda(dictionary_creator)

# output_parser=StrOutputParser()

# chain1_industry=social_media_template | llm | output_parser

# print(chain1_industry.invoke({"industry":"Sustainability/Green technology"}))

# print("===========================")
# social_media_post_template=ChatPromptTemplate.from_messages(
#     [
#         ("system","You are a expert social media content creator"),
#         ("user","Generate a intersting social media content on {topic} topic")
#     ]
# )

# def dictionary_creator_topic(text:str):
#     return {"topic":text}

# runnable_dict_topic=RunnableLambda(dictionary_creator_topic)
# chain2_content=social_media_post_template | llm | output_parser

# final_chain=chain1_industry | dictionary_creator_topic | chain2_content

# print(final_chain.invoke({"industry":"Sustainability/Green technology with AI"}))