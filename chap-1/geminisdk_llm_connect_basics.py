# pip install google-genai
# pip install python-dotenv
# api key

from google import genai
from dotenv import load_dotenv
from google.genai import types
import httpx

load_dotenv(override=True)
http_option=types.HttpOptions(httpx_client=httpx.Client(verify=False))

client=genai.Client(http_options=http_option)

model=client.models.generate_content(
    model="gemini-3.6-flash",
    contents=["fact about gpu"]
)


response= model.text

print(response)
