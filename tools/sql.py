import sqlite3
from pydantic.v1 import BaseModel
from typing import List
from langchain.tools import Tool

conn  = sqlite3.connect('db.sqlite')

class RunQueryArgsSchema(BaseModel):
    query: str

class DescribeTableArgsSchema(BaseModel):
    table_names: List[str]

def list_tables():
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
    rows = c.fetchall()
    return "\n".join([row[0] for row in rows])

def run_sqlite_query(query: str):
    c = conn.cursor()
    try:
        c.execute(query)
        return c.fetchall()
    except sqlite3.OperationalError as e:
        return (f"The following error occurred: {str(e)}")
    
def describe_table(table_names: str):
    c = conn.cursor()
    tables = ', '.join("'" + item + "'" for item in table_names)
    rows = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name IN ({tables});")
    return '\n'.join(row[0] for row in rows if row[0] is not None)

run_sqlite_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Use this to run a query against the database",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema,
)

describe_table_tool = Tool.from_function(
    name="describe_table",
    description="Use this to describe a table in the database",
    func=describe_table,
    args_schema=DescribeTableArgsSchema,
)

tools = [run_sqlite_query_tool, describe_table_tool]