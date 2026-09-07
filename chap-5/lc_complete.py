# llmcall, custom tool, tool invocation, pydantic
import os
from typing import List, Optional
from dotenv import load_dotenv

# Pydantic Validation & Structured Output
from pydantic import BaseModel, Field

# LangChain Core & OpenAI Integrations
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
import httpx

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

# define pydantic model for tool
class Calculator(BaseModel):
    expression:str=Field(description="The matematical expression to evaluate")

# defnie pydandic model for final response from llm
class AgentOutput(BaseModel):
    final_answer:str
    tool_calls:List[str]
    confidence_score:float

# tool to evaluate expression
@tool(args_schema=Calculator)
def evaluate_expression(expression:str)->str:
    """to evaluate any given mathematical expression"""
    return eval(expression)

prompt=ChatPromptTemplate.from_messages([
    ("system","You are an expert agent and exposed with expression evaluator tool, make use of it whenever required"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user","{user_query}"),
    MessagesPlaceholder(variable_name="agent_scratchcard")

])

chat_history=[]
agent_scratchcard=[]

tool_kit=[evaluate_expression]
toolname_map={t.name:t for t in tool_kit}



llm_with_tools=llm.bind_tools(tool_kit)
messages=prompt.format_messages(user_query="I bought a 100 products and each is 34$ what is the total spent amount?",
                                chat_history=chat_history,
                                agent_scratchcard=agent_scratchcard)

response_only_llm=llm.invoke(messages)

print(response_only_llm)

response=llm_with_tools.invoke(messages)
agent_scratchcard.append(response)
print("====================================")
print(response)

for tool_call in response.tool_calls:
    tool_name=tool_call["name"]
    tool_args=tool_call["args"]
    print("Using this tool:",tool_name)

    selected_tool=toolname_map.get(tool_name)
    if selected_tool:
        tool_response=selected_tool.invoke(tool_args)
        print(tool_response)
        agent_scratchcard.append(ToolMessage(content=tool_response,tool_call_id=tool_call["id"]))

messages=prompt.format_messages(user_query="summarize the llm calls made with tools",
                                chat_history=chat_history,
                                agent_scratchcard=agent_scratchcard
                                )

final_response=llm.invoke(messages)
print(final_response)