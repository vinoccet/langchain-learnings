from typing import TypedDict,Sequence,Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,AIMessage,HumanMessage,BaseMessage
import os
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv(override=True)
http_client=httpx.Client(verify=False)


class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]

@tool
def add_tool(a:int,b:int):
    """"used to add 2 given numbers"""
    return a+b
tools=[add_tool]

llm=ChatOpenAI(
    model="gemini-2.0-flash-thinking-exp-01-21",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
).bind_tools(tools, tool_choice="auto")

def model_call(state:AgentState)->AgentState:
    system_message=SystemMessage(content="you are my AI assisstant, please answer to my queries with your best ability")
    response=llm.invoke([system_message]+state["messages"])
    return {"messages":[response]}

def should_contain(state:AgentState):
    messages=state["messages"] 
    last_message=messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
graph=StateGraph(AgentState)
graph.add_node("agent1",model_call)
tool_node=ToolNode(tools=tools)
graph.add_node("tools",tool_node)

graph.add_edge(START,"agent1")
graph.add_conditional_edges("agent1",
                            should_contain,
                            {
                                "continue":"tools",
                                "end":END
                            }
                            )
graph.add_edge("tools","agent1")
compiled_grapg=graph.compile()

def print_stream(stream):
    for a in stream:
        message=a["messages"][-1]
        print(message)
input={"messages":[("user","Add 40 plus 20 and tell interisting fact")]}
print_stream(compiled_grapg.stream(input,stream_mode="values"))