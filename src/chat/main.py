
import warnings
import os
warnings.filterwarnings('ignore')

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import ChatOllama
from langchain_openai import OpenAI
from data.engine import get_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv(find_dotenv())

engine = get_engine()

db = SQLDatabase(engine=engine)
# llm = OllamaLLM(model="mistral:latest", base_url="localhost:11434", api_key="...")
# llm = OpenAI(model="Mistral-7B-Instruct-v0.3-GGUF", base_url="localhost:3011", api_key="...")
# llm = ChatOllama(model="mistral:latest", base_url='localhost:11434')
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = os.getenv("GEMINI_API_KEY")
    # other params...
)

toolkit= SQLDatabaseToolkit(db=db, llm=llm)
context = toolkit.get_context()
tools = toolkit.get_tools()
# print(len(tools))
# print(list(context))
# print(context["table_info"])


from langchain import hub
prompt_template = """
system
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.
table sec means security or stock
table trans_item stored daily transaction summary
table sec_ma store the information about moving average value, ma5 stands for the 5 days moving average price, ma10 stands for 10 days moving average price and so on.
when the human want to search one or more securities moving average price, many they only provide the security name, you need to find the security code first, then execut query with sec_ma table.
if ma10 greater than ma5, it stands for the security price is going up in recent days,  vice versa
"""
# assert len(prompt_template.messages) == 1
# print(prompt_template.input_variables)

system_message = prompt_template.format(dialect="postgresql", top_k=5)

from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(
    llm, toolkit.get_tools(), state_modifier=system_message
)

example_query = "how many records are there in sec_info table?"
example_query = "list all records of trans_item which code is 002730, and sort by date with decending order"
example_query = "请列出电光科技的5均线数据"
example_query = "请列出30均线大于10日均线股票名称"

events = agent_executor.stream(
    {"messages": [("human", example_query)]},
    stream_mode="values"
)

for event in events:
    event["messages"][-1].pretty_print()

# from langchain_community.agent_toolkits.sql.prompt import SQL_FUNCTIONS_SUFFIX
# from langchain_core.messages import AIMessage, SystemMessage
# from langchain_core.prompts.chat import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )

# messages = [
#     HumanMessagePromptTemplate.from_template("{input}"),
#     AIMessage(content=SQL_FUNCTIONS_SUFFIX),
#     MessagesPlaceholder(variable_name="agent_scratchpad"),
# ]

# prompt = ChatPromptTemplate.from_messages(messages)
# prompt = prompt.partial(**context)

# from langchain.agents import create_openai_tools_agent, create_sql_agent
# from langchain.agents.agent import AgentExecutor


# agent = create_sql_agent(llm=llm, db=db, tools=sql_tool_kit.get_tools(), prompt=prompt)
# # agent_executor = AgentExecutor(
# #     agent=agent,
# #     tools=sql_tool_kit.get_tools(),
# #     verbose=True,
# # )

# # resp = agent_executor.invoke({"input": "Describe the schema of the sec table"})
# # print(resp)