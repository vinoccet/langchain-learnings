from typing import TypedDict
from langgraph.graph import StateGraph,END

# print the name and wish 

# create a sharable mutable state
class MessagingState(TypedDict):
    name:str
    message:str

# create node    
def greet(state:MessagingState)->MessagingState:
    """sends a greeting message to the user"""
    greet= f"hello, {state["name"]} have a great day"
    state["message"]=greet
    return state

# add node to graph
graph=StateGraph(MessagingState)
graph.add_node("greet",greet)

# establich connection
graph.set_entry_point("greet")
graph.add_edge("greet",END)

# compile the graph
compiled_graph=graph.compile()

print(compiled_graph.get_graph().draw_ascii())

response=compiled_graph.invoke({"name":"vinoth"})
print(response)