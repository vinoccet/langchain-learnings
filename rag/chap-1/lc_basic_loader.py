from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import httpx
from langchain_openai import ChatOpenAI
import os
# pip install langchain_chroma

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
# pdfs, docs, drive, slack etc
from langchain_core.output_parsers import StrOutputParser

doc_text="""Cognizant was established in 1994 in Chennai, India, as Dun & Bradstreet Satyam Software (DBSS), a 76:24 joint venture between Dun & Bradstreet and Satyam Computers, with Kumar Mahadeva, and Srini Raju as the founding CEOs and MDs.[8][9] It began with 50 employees in Chennai as Dun & Bradstreet's in-house technology unit focused on implementing large-scale IT projects for Dun & Bradstreet businesses.[10] In 1996, the company started pursuing customers beyond Dun & Bradstreet.[11]

In 1996, Dun & Bradstreet spun off several of its subsidiaries, including Erisco, IMS International, Nielsen Media Research, Pilot Software, Strategic Technologies and DBSS, to form a new company called Cognizant Corporation, headquartered in Chennai, India. Three months later, in 1997, DBSS renamed itself Cognizant Technology Solutions. In July 1997, Dun & Bradstreet bought Satyam's 24% stake in DBSS for $3.4 million.[12][13] Headquarters were moved to the United States, and in March 1998, Kumar Mahadeva was named CEO.[14] Operating as a division of the Cognizant Corporation, the company focused on Y2K-related projects and web development.[15] In 1998, the parent company, Cognizant Corporation, split into two companies: IMS Health and Nielsen Media Research.[16] After this restructuring, Cognizant Technology Solutions became a public subsidiary of IMS Health. In June 1998, IMS Health partially spun off the company, conducting an initial public offering of the Cognizant stock."""

print(len(doc_text))
document=Document(page_content=doc_text,meta_data={"source":"cognizant wiki","doc_id":"01"})

# splitting
splits=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

chunks=splits.split_documents([document])

print(len(chunks))
print(chunks)

http_client=httpx.Client(verify=False)
load_dotenv()

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

# embeddings
embed_function=OpenAIEmbeddings(model="text-embedding-3-small",http_client=http_client)

# sample_embed=embed_function.embed_documents(["cat", "kitten"])

# embeddings=[]
# for chunk in chunks:
#     emeded_doc=embed_function.embed_documents([chunk])
#     embeddings.append(emeded_doc)

# stores to vector db
vector_db=Chroma.from_documents(documents=chunks,embedding=embed_function)

# matched_chunks=vector_db.similarity_search("who is cognizant founder and when it was inagurated in USA?",k=2)

# response=llm.invoke(f"who is cognizant founder and when it was inagurated in USA?, you check the following context{matched_chunks}")

# print(response)

# retreive chunks and pass as context to llm

retreiver=vector_db.as_retriever(search_kwargs={"k":2})

template="""Understand the given context {context} answer the following question {question} and dont go out of context"""

prompt=ChatPromptTemplate.from_template(template)

# retreiver | prompt | llm | output

def doc2str(docs):
    return "\n\n".join(doc.page_content for doc in docs)

output_parser=StrOutputParser()

rag_chain = (
    {"context":retreiver | doc2str, "question":RunnablePassthrough()} | prompt | llm | output_parser
)

print(rag_chain.invoke("Who started cognizant and what was its first name?"))