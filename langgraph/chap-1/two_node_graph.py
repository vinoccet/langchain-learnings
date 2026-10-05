# get last 5 trasactions from the user and give verdict("saver" or "spender") based on the trasactions
from typing import TypedDict
from langgraph.graph import StateGraph,END

# define trasaction state
class TransactionState(TypedDict):
    name:str
    transactions:list[int]
    verdict:str

def get_user_name_node(state:TransactionState)->TransactionState:
    """To get the user name and store it in state"""
    print("Enter the user name:")
    state["name"]=input(">>")
    return state

def get_transactions_node(state:TransactionState)->TransactionState:
    """get last 5 transactions detaials as comma seperated values and update state"""
    print("Enter last 5 transaction amounts:")
    transaction_input=input(">>")
    state["transactions"]=(int(t.strip()) for t in transaction_input.split(","))
    return state

def analyze_transction_node(state:TransactionState)->TransactionState:
    """sum up all the trascations if the sum is grater than 0 verdict is saver"""
    trsanctions_sum=sum(state["transactions"])
    state["verdict"]="SAVER" if trsanctions_sum>0 else "SPENDER"
    return state

# create state graph
transaction_graph=StateGraph(TransactionState)

# add nodes
transaction_graph.add_node("get_user_name_node",get_user_name_node)
transaction_graph.add_node("get_transactions_node",get_transactions_node)
transaction_graph.add_node("analyze_transction_node",analyze_transction_node)

# establish connection
transaction_graph.set_entry_point("get_user_name_node")
transaction_graph.add_edge("get_user_name_node","get_transactions_node")
transaction_graph.add_edge("get_transactions_node","analyze_transction_node")
transaction_graph.add_edge("analyze_transction_node",END)

# compile graph
compiled_graph=transaction_graph.compile()

print(compiled_graph.get_graph().draw_ascii())

print(compiled_graph.invoke({}))