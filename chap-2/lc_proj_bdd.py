# llm call through langchain, different roles and messages and dynamic prompt
# input : feature description , 
# output : Feature, scenario, given, when, then - gherkin syntax

from dotenv import load_dotenv
import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
http_client=httpx.Client(verify=False)

llm=ChatOpenAI(
          model="poolside/laguna-s-2.1",
    base_url="https://inference.poolside.ai/v1",
    api_key=os.getenv("POOLSIDE_API_KEY"),
    http_client=http_client  ,
    
)

# Login Feature - SauceDemo

# ```gherkin
# Feature: User Login
#   As a registered user
#   I want to log in to the SauceDemo application
#   So that I can access the inventory page and browse products

#   Background:
#     Given I am on the SauceDemo login page

#   Scenario: Successful login with valid credentials
#     When I enter username as "standard_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should be redirected to the inventory page
#     And I should see the products list
#     And I should see the sidebar menu

#   Scenario: Login attempt with empty username field
#     When I enter password as "secret_sauce"
#     And I click the login button
#     Then I should see an error message indicating "Username is required"
#     And I should remain on the login page

#   Scenario: Login attempt with empty password field
#     When I enter username as "standard_user"
#     And I click the login button
#     Then I should see an error message indicating "Password is required"
#     And I should remain on the login page

#   Scenario: Login attempt with both fields empty
#     When I click the login button
#     Then I should see an error message indicating "Username is required"
#     And I should remain on the login page

#   Scenario: Login attempt with invalid username
#     When I enter username as "invalid_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should see an error message indicating "Username and password do not match"
#     And I should remain on the login page

#   Scenario: Login attempt with invalid password
#     When I enter username as "standard_user"
#     And I enter password as "wrong_password"
#     And I click the login button
#     Then I should see an error message indicating "Username and password do not match"
#     And I should remain on the login page

#   Scenario: Login attempt with locked out user account
#     When I enter username as "locked_out_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should see an error message indicating "User has been locked out"
#     And I should remain on the login page

#   Scenario: Login with performance glitch user account
#     When I enter username as "performance_glitch_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should be redirected to the inventory page
#     And I should see the products list

#   Scenario: Login with problem user account
#     When I enter username as "problem_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should be redirected to the inventory page
#     And I should see the products list

#   Scenario: Login with visual user account
#     When I enter username as "visual_user"
#     And I enter password as "secret_sauce"
#     And I click the login button
#     Then I should be redirected to the inventory page
#     And I should see the products list
# ```

# ## Notes on Implementation Considerations:

# - **Environment**: Ensure tests run against the correct SauceDemo URL (https://www.saucedemo.com/)
# - **Valid Credentials**: 
#   - Standard users: `standard_user` / `secret_sauce`
#   - Locked out user: `locked_out_user` / `secret_sauce`
#   - Performance glitch user: `performance_glitch_user` / `secret_sauce`
#   - Problem user: `problem_user` / `secret_sauce`
#   - Visual user: `visual_user` / `secret_sauce`
# - **UI Elements**: Verify proper handling of form fields, error messages, and redirect behavior
# - **Error Messages**: Validate exact error message text matches SauceDemo's actual error messages
# - **Browser Compatibility**: Consider running scenarios across different browsers if needed
# - **Performance**: Account for potential delays with performance_glitch_user account
# - **Session Management**: Ensure proper cleanup between scenarios to avoid session conflicts

few_shot_bdd=[
    HumanMessage(content="Generate a bdd content using gherkin syntax for the given feature description saucedemo.com"),
AIMessage(content="""
Feature: User Login
  As a registered user
  I want to log in to the SauceDemo application
  So that I can access the inventory page and browse products

  Scenario: Successful login with valid credentials
    Given I am on the SauceDemo login page
    When I enter username as "standard_user"
    And I enter password as "secret_sauce"
    And I click the login button
    Then I should be redirected to the inventory page
    And I should see the products list
    And I should see the sidebar menu
""")
]

bdd_template= ChatPromptTemplate.from_messages([
    ("system","You are a expert QA engineer responsible for bdd content"),
    *few_shot_bdd,
    ("human", "Generate a bdd content using gherkin syntax for the given feature description {feature_description}")
])

bdd_formated_prompt=bdd_template.format_messages(
feature_description="Login feature for https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
)

print(bdd_formated_prompt)

response=llm.invoke(bdd_formated_prompt)

print(response.content)