# Imports
import sqlite3 # To connect to the local SQLite database
import pandas as pd # So query results can be handled as DataFrames
from langchain.tools import tool # Tool is just a python function, until decorated with @tool, there LangChain allows the agent decide when to call it

DB_PATH = "tool_files/olist.db" # Where the SQLite database is located. Its stored in tool_files to keep data-related things separate from app logic

# get schema tool
# Gives the agent info about what tables and columns exist in the database before writing SQL
@tool
def get_schema(): # the docstring is important because it tells the agent when and why to use the tool, LangChain uses it to help the model decide the relevance of the tool
    """
    Use this tool when Ollie needs to understand the database structure before writing SQL.
    This tool returns:
    - table names
    - column names
    - a few sample rows
    Use it before generating SQL or whenever the user asks about a table, metric,
    or column that needs confirmation.
    """
    print("Ollie is using get_schema.")

    conn = sqlite3.connect(DB_PATH) # Opens a connection to the local olist SQLite db

    try:
        cursor = conn.cursor()

        # Get all tables
        # SQL query that asks the database for all table names
        # The result is stored in a list called 'tables'
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            return "No tables found in the database."

        output = []
        # For each table, the tool uses PRAGMA table_info to retrieve column names, giving Ollie the structure of each table
        for table in tables:
            output.append(f"\nTABLE: {table}")

            # Get columns
            cursor.execute(f"PRAGMA table_info({table});")
            cols = cursor.fetchall()
            col_names = [col[1] for col in cols]
            output.append("Columns: " + ", ".join(col_names))

            # Sample rows
            # Tool also retrieves a few sample rows from each table
            # Helps Ollie understand the type of values in each column, not just column names
            try:
                sample_df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 3", conn)
                output.append("Sample rows:")
                output.append(sample_df.to_string(index=False))
            except Exception as e:
                output.append(f"Could not fetch sample rows: {str(e)}")

        return "\n".join(output)
    # Function includes error handling - something goes wrong, the app returns error message instead of crashing
    # finally block closes the database connection every time
    except Exception as e:
        return f"Schema error: {str(e)}"
    finally:
        conn.close()

# validate sql tool
# The tool checks whether a SQL query is safe before executed
@tool
def validate_sql(sql_query: str):
    """
    Use this tool to validate a SQL query before execution.
    This tool checks whether:
    - the query is a SELECT query or a read-only CTE beginning with WITH
    - it does not contain dangerous commands such as DROP, DELETE, UPDATE, INSERT, ALTER, or CREATE
    Use this tool before running SQL.
    """
    print("Ollie is using validate_sql.")
    print(sql_query)
    # First, query is converted to uppercase and checks whether it starts with SELECT
    # Ensures Ollie can only read data, not modify it
    query_upper = sql_query.strip().upper()

    if not query_upper.startswith(("SELECT", "WITH")):
        return "Invalid query: only read-only SELECT queries are allowed."
    # Checks for dangerous keywords like DROP or DELETE - If found, it rejects the query
    banned_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
    for keyword in banned_keywords:
        if keyword in query_upper:
            return f"Invalid query: contains forbidden keyword '{keyword}'."
    # Ollie gets confirmation that its safe to execute
    return "SQL query is valid."

# run sql tool
# Once ollie has a valid SELECT query, a tool runs it against the SQLite db and returns results
@tool
def run_sql(sql_query: str):
    """
    Use this tool to execute a validated SELECT SQL query on the Olist SQLite database.
    This tool should be used only after the SQL has been written and validated.
    It returns query results as a table-like string.
    Only read-only SELECT queries, including CTE-based SELECT queries, are allowed.
    """
    print("Ollie is using run_sql.")
    print(sql_query)
    # Second safety layer to validate only SELECT queries are allowed
    query_upper = sql_query.strip().upper()

    if not query_upper.startswith(("SELECT", "WITH")):
        return "Only read-only SELECT queries are allowed."
    # Tool opens the db connection and uses read_sql_query to execute the query
    # Tables are returned in a table format so Ollie can include them in the final response
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql_query, conn)
        return df.to_string(index=False)
    # If the generated SQL has an issue, tool returns the error message instead of crashing
    except Exception as e:
        return f"Query error: {str(e)}"
    finally:
        conn.close()