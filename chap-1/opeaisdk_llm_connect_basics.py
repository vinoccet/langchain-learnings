# python -m venv .venv
# SDK and why require LC

# pip install openai
# pip install python-dotenv
# api key

from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx

http_client=httpx.Client(verify=False)
load_dotenv()
print(os.getenv("OPENAI_API_KEY")[:3])

client=OpenAI(
    http_client=http_client
)

print(client.models.list())
# roles: user, system, Ai assistance role

model=client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"say hi"},{"role":"system","content":"reply in 1 word"}]
)

print(model)
print(model.choices[0].message.content)

