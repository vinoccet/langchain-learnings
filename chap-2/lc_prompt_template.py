from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import httpx
import os

from langchain_core.prompts import PromptTemplate,ChatPromptTemplate

from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)


# template="Provide me a {tone} fact about {city}"

# prompt_template=PromptTemplate.from_template(template)
# formated_prompt=prompt_template.format(tone="fun",city="chennai")

# print(formated_prompt)

template=ChatPromptTemplate.from_messages([
    ("system","Reply me with the {tone} tone"),
    ("human","Tell interesting fact about {topic}")
]
)

formated_prompt=template.format_messages(
    tone="fun",
topic="llm"
)
response=llm.invoke(formated_prompt).content

print(response)

