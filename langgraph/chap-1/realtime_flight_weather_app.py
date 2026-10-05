import requests
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os
import httpx
from dotenv import load_dotenv
from typing import TypedDict,Annotated,Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,SystemMessage,AIMessage,HumanMessage
load_dotenv()
http_client=httpx.Client(verify=False)
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def get_flight_details(
    departure_id: str,         # Airport code (Austin-Bergstrom International)
    arrival_id: str,           # Airport code (Los Angeles International)
    outbound_date: str, # Date in YYYY-MM-DD format
    return_date: str,   # Optional: Include for round-trip flights
    currency: str,             # Optional: Currency definition
)->str:
    """get the best or cheap flights for the given details
    
    Args:
    departure_id: str,         # 3 letter Airport code example : MAA, SIN
    arrival_id: str,           # 3 letter Airport code example : MAA, SIN
    outbound_date: str, # departure Date in YYYY-MM-DD format
    return_date: str,   # arrival date in YYYY-MM-DD format Include for round-trip flights
    currency: str,             # 3 letter currency code example: INR, USD
    
    """

    SERPAPI_API_KEY = os.getenv("SERP_API_KEY")
    flight_summary=[]

# 2. Configure the Google Flights search parameters
# Required: engine, departure_id, arrival_id, outbound_date
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,         # Airport code (Austin-Bergstrom International)
        "arrival_id": arrival_id,           # Airport code (Los Angeles International)
        "outbound_date": outbound_date, # Date in YYYY-MM-DD format
        "return_date": return_date,   # Optional: Include for round-trip flights
        "currency":currency,             # Optional: Currency definition
        "hl": "en",                    # Optional: Language profile
        "api_key": SERPAPI_API_KEY
    }
    
        # 3. Make the GET request to SerpApi's central endpoint
    print("Fetching flight data from SerpApi...")
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    
    # 5. Extract and print flight details
    # SerpApi categorizes results into 'best_flights' and 'other_flights'
    best_flights = data.get("best_flights", [])
    
    if not best_flights:
        print("No flight information found or check your parameters.")
        flight_summary.append("No flight information found or check your parameters.")
    else:
        print(f"\n--- Top {len(best_flights)} Best Flight Options ---")
        for index, itinerary in enumerate(best_flights, start=1):
            price = itinerary.get("price")
            total_duration = itinerary.get("total_duration")
            
            print(f"\nOption #{index}: Total Price: ${price} | Duration: {total_duration} mins")
            flight_summary.append(f"\n Option #{index}: Total Price: ${price} | Duration: {total_duration} mins")
            # A single itinerary option can contain layovers (multiple leg flights)
            for leg in itinerary.get("flights", []):
                airline = leg.get("airline")
                flight_number = leg.get("flight_number")
                dep_airport = leg.get("departure_airport", {}).get("id")
                dep_time = leg.get("departure_airport", {}).get("time")
                arr_airport = leg.get("arrival_airport", {}).get("id")
                arr_time = leg.get("arrival_airport", {}).get("time")
                flight_summary.append(f"   flights details:[✈️ airline: {airline} ({flight_number}), departure airport(departure time): {dep_airport} ({dep_time}) -> {arr_airport} ({arr_time})]")
                print(f"  ✈️ {airline} ({flight_number}): {dep_airport} ({dep_time}) -> {arr_airport} ({arr_time})")


    return "\n".join(flight_summary)

def get_hotel_details(query:str)->str:
    search=DuckDuckGoSearchRun()
    return search.run(f"get best hotel for {query}")

tools=[get_flight_details]
llm=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
).bind_tools(tools)

# create an agent state
class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]
    user_query:str
    flight_result:str
    hotel_result:str
    itenary:str

# create nodes

def model_call(state:AgentState)->AgentState:
    system_prompt=SystemMessage(content="You are an AI assistant, reply to my queries in a best possible way, have also exposed tools")
    response=llm.invoke([system_prompt]+[HumanMessage(content=state["user_query"])])
    return {"flight_result":response.content,"messages":[response]}

tool_node=ToolNode(tools)

def hotel_details(state:AgentState)->AgentState:
    return{
        "hotel_result":get_hotel_details(state["user_query"]),
         "messages":[AIMessage(content="returned hotel details")]
    }

def itenary(state:AgentState)->AgentState:
    print("** invoking itenary agent***")
    print(f"the state query is: {state["user_query"]}  ")
    print(f"the flight result: {state["flight_result"]}")
    print(f"the hotel result: {state["hotel_result"]}")
    prompt=f""""
    prepare me an travel itenary for below details:

    user query:{state["user_query"]}

    flight details: {state["flight_result"]}
    
    hotel details: {state["hotel_result"]} 
     
    """    
    system_prompt="you are an seasoned travel planner"
    response=llm.invoke([SystemMessage(content=system_prompt),
                         HumanMessage(content=prompt)])
    return {"itenary":response.content,
    "messages":[response]
    }

def final_agent(state:AgentState)->AgentState:
    prompt=f"""
    Generate final travel response.

    Flights:
    {state["flight_result"]}

    Hotels:
    {state["hotel_result"]}

    Itinerary:
    {state["itenary"]}
"""
    response=llm.invoke([HumanMessage(content=prompt)])
    return {
        "messages":[response]
    }
def should_continue(state:AgentState):
    messages=state["messages"]
    last_message=messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "hotel_agent"

# build graph
graph=StateGraph(AgentState)
graph.add_node("flightagent",model_call)
graph.add_node("tools",tool_node)
graph.add_node("hotel_agent",hotel_details)
graph.add_node("itenary_agent",itenary)
graph.add_node("final_agent",final_agent)


graph.add_edge(START,"flightagent")
graph.add_edge("flightagent","tools")
graph.add_edge("tools","hotel_agent")
graph.add_edge("hotel_agent","itenary_agent")
graph.add_edge("itenary_agent","final_agent")
graph.add_edge("final_agent",END)

# compile graph
app=graph.compile()

input_query={"user_query":"Planning a travel to dubai on october 22 year 2026 get the best flight details from coimbatore and plan the itenary with complete plan"}
stream_response=app.stream(input_query,print_mode="values")
print(stream_response)

for s in stream_response:
    # Check if 'messages' key exists before accessing
    if "messages" in s and s["messages"]:
        message = s["messages"][-1]
        print(f"Final response {message}")
    else:
        print(f"Step output: {s}")