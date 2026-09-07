# Task 7: Building and Binding a Custom Python Tool

# Objective: Write a custom decorated function tool and bind it to a model.

# Instructions: Write a custom Python function (e.g., calculating password complexity score) 
# decorated with @tool and a descriptive docstring. Bind this function to your chat model using .
# bind_tools(), pass a test query that triggers it, and inspect the resulting 
# .tool_calls dictionary on the AIMessage.