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

# ==========================================
# 1. PYDANTIC VALIDATION & STRUCTURED OUTPUT
# ==========================================

class CalculationInput(BaseModel):
    """Pydantic schema to validate tool arguments."""
    expression: str = Field(description="A valid mathematical expression to evaluate, e.g., '145 * 32'")

class AgentResponseSchema(BaseModel):
    """Pydantic schema enforcing final structured output from the agent."""
    final_answer: str = Field(description="The clear, human-readable answer to the user's request.")
    tools_used: List[str] = Field(description="List of tools that were invoked during the reasoning process.")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0.")


# ==========================================
# 2. DEFINE TOOLS WITH PYDANTIC SCHEMAS
# ==========================================

@tool(args_schema=CalculationInput)
def evaluate_math(expression: str) -> str:
    """Evaluates a mathematical expression safely using python eval."""
    try:
        # Safe evaluation of basic math
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters found in mathematical expression."
        
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# Bundle tools
tools = [evaluate_math]
tool_map = {t.name: t for t in tools}


# ==========================================
# 3. LLM INITIALIZATION & PROMPT TEMPLATES
# ==========================================

# Initialize the LLM and bind tools to it
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
    model="gemini-3.6-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    http_client=http_client
)
llm_with_tools = llm.bind_tools(tools)

# Define prompt templates with message handling placeholders
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an advanced, helpful assistant equipped with calculation tools. "
               "Analyze the user request, call tools if necessary, and synthesize your final output."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


# ==========================================
# 4. MESSAGE HANDLING & AGENT RUNTIME LOOP
# ==========================================

def run_agentic_workflow(user_query: str, chat_history: list = None) -> AgentResponseSchema:
    if chat_history is None:
        chat_history = []
        
    scratchpad = []
    
    # Format the prompt using template variables
    messages = prompt.format_messages(
        chat_history=chat_history,
        input=user_query,
        agent_scratchpad=scratchpad
    )
    
    # First LLM Call: Decide whether to call tools or respond directly
    response = llm_with_tools.invoke(messages)
    tools_called = []
    
    # Handle Tool Calling loop if the model requests tool executions
    while response.tool_calls:
        scratchpad.append(response) # Append AI message containing tool calls
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tools_called.append(tool_name)
            
            print(f"\n[Tool Execution] Calling tool '{tool_name}' with args: {tool_args}")
            
            # Execute the tool
            selected_tool = tool_map.get(tool_name)
            if selected_tool:
                tool_result = selected_tool.invoke(tool_args)
            else:
                tool_result = f"Error: Tool {tool_name} not found."
                
            print(f"[Tool Result] {tool_result}")
            
            # Append Tool Message back into scratchpad
            scratchpad.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
            
        # Re-invoke LLM with updated scratchpad context
        messages = prompt.format_messages(
            chat_history=chat_history,
            input=user_query,
            agent_scratchpad=scratchpad
        )
        response = llm_with_tools.invoke(messages)

    # ==========================================
    # 5. STRUCTURED OUTPUT VALIDATION
    # ==========================================
    # Force the final text response to map to our Pydantic schema using .with_structured_output()
    structured_llm = llm.with_structured_output(AgentResponseSchema)
    
    final_prompt = f"Summarize this final text response into the requested structured schema. User query was: '{user_query}'. Assistant raw answer: '{response.content}'"
    
    structured_output = structured_llm.invoke(final_prompt)
    
    # Fallback or patch tracked metadata if needed
    structured_output.tools_used = list(set(tools_called))
    return structured_output


# ==========================================
# 6. EXECUTION DEMO
# ==========================================
if __name__ == "__main__":
    print("--- Starting Agentic Application Live Demo ---")
    
    query = "If I buy 145 items at $32 each, what is my total cost?"
    print(f"User Query: {query}")
    
    # Run the application
    result = run_agentic_workflow(user_query=query)
    
    print("\n--- Structured Output Validation Results (Pydantic) ---")
    print(f"Final Answer    : {result.final_answer}")
    print(f"Tools Used      : {result.tools_used}")
    print(f"Confidence Score: {result.confidence_score}")