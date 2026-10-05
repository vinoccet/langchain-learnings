from typing import TypedDict,List,Union
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,AIMessage
import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
)

# create a cli based llm chatbot with memory

#step 1: create agent state
class AgentState(TypedDict):
    messages:List[Union[HumanMessage,AIMessage]]

#step 2: create node to process and invoke llm
def process_llm(state:AgentState)->AgentState:
    response = llm.invoke(state["messages"])
    print(f"AI response is : {response.content}")
    return {"messages":state["messages"]+[AIMessage(content=response.content)]}

#step 3: create grpah
graph=StateGraph(AgentState)

#step4: add nodes to the stategraph
graph.add_node("process_llm",process_llm)

#step5: create edges and connect nodes
graph.add_edge(START,"process_llm")
graph.add_edge("process_llm",END)

#step6: compile the created graph
compiled_graph=graph.compile()

print("Welcome to the chatbot with memory!!!!")
# step6: get user input
user_query=input(">>")

# step 7 : create logic for conversation history
conversation_history=[]

while user_query!="exit":
    conversation_history.append(HumanMessage(content=user_query))
    graph_response=compiled_graph.invoke({"messages":conversation_history})
    conversation_history=graph_response["messages"]
    user_query=input(">>")

print(conversation_history)