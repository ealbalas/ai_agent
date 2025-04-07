import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from tools.sql import run_sqlite_query_tool, list_tables, describe_table_tool
from tools.report import write_report_tool
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

tools = [
    run_sqlite_query_tool, 
    describe_table_tool, 
    write_report_tool
    ]

chat = ChatOpenAI()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

tables = list_tables()
prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(
            f"You are a helpful assistant that has access to a SQLite database.\n"
            f"The database has tables of: {tables}\n"
            "Do not make any assumptions about the table names. If you need to know more about a table, use the describe_table tool.\n"
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ],
    input_variables=["input"],
    partial_variables={"format_instructions": "{format_instructions}"},
)

agent = OpenAIFunctionsAgent(
    llm=chat,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    memory=memory,
)

# agent_executor("How many users are in the database?")
# agent_executor("How many users have an address in the database?")
# agent_executor("Summurize the top 5 most popular products in the database? Write the results to a report file.")
agent_executor(
    "How many orders are there? Write the result to an HTML report file."
)
agent_executor(
    "Repeat the exact same process for users"
)