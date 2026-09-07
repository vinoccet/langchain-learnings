# zero shot, few shot prompts, cot - user prompts
# Systemprompts
# AI messages

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import httpx
import os

from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

messages=[
    SystemMessage(content="Reply me in a funny way"),
    HumanMessage(content="Give me a leave letter with 2 sentences as i am sick")
]

# """
# "Subject: Leave Application Due to Illness\n\nDear [Recipient's Name],\n\nI am writing to inform you that I have been unwell and am currently unable to attend to my duties. I request you to kindly grant me leave for the necessary period to recover and would be grateful for your consideration."
# """

response=llm.invoke(messages)

print(response)