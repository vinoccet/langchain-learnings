from typing import TypedDict,Annotated,Sequence
from langgraph.graph import StateGraph,END,START
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage,BaseMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

http_client=httpx.Client(verify=False)

class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]

@tool
def add_tool(a:int,b:int):
    """provide the addition of given 2 numbers"""
    return a+b
tools=[add_tool]

llm=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
).bind_tools(tools)

def model_call(state:AgentState)->AgentState:
    system_prompt=SystemMessage(content="You are an helpful AI assistant, reply me with the relavant answer to maximum possible for given query")
    response=llm.invoke([system_prompt]+state["messages"])
    return {"messages":[response]}

def should_continue(state:AgentState):
    messages=state["messages"]
    last_message=messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

tool_node=ToolNode(tools)

graph=StateGraph(AgentState)
graph.add_node("agent1",model_call)
graph.add_node("tools",tool_node)

graph.add_edge(START,"agent1")
graph.add_conditional_edges("agent1",should_continue)

app=graph.compile()

input={"messages":[("user","what is the sum of 10 plus 20 and provide some intersting fact")]}

agent_response=app.invoke(input)
print(agent_response)