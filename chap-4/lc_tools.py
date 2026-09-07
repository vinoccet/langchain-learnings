from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from langchain.agents import create_agent
import httpx
import os

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun


load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

# create tools
# create tool 1
websearch_tool=DuckDuckGoSearchRun()

# print(websearch_tool.invoke("What is the weather in chennai today?"))
# create tool 2
api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1000)
wikipedia_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# official tools
@tool(description="this returns the mathematical evaluation of a given expression")
def calculator(exp:str):
    """this returns the mathematical evaluation of a given expression"""
    return eval(exp)

@tool
def send_email(value:str):
    """This tool sends email to the recipient"""
    return "Email sent successfully"
# create agent
tools_kit=[websearch_tool,wikipedia_tool,calculator,send_email]


agent=create_agent(
    model=llm,
    tools=tools_kit
)

# response=agent.invoke({
#     "messages":[("user","what is the current weather in coimbatore?")]
# })

events= agent.stream(
    {
    "messages":[("user","you are a useful assistant and exposed to tool calls,see whether you can use tool, Send an email to my mail id")]
},
stream_mode="values"
)

for event in events:
    print(event["messages"][-1])
