from langchain_community.tools import DuckDuckGoSearchRun

# Initialize the tool
search = DuckDuckGoSearchRun()

# Run a query
response = search.run("Best hotels in Dubai, provide only hotel names and rating")
print(response)