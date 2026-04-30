import sqlite3
import pandas as pd
from langchain.tools import tool

DB_PATH = "tool_files/olist.db"

#get schema tool
@tool
def get_schema():
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

    conn = sqlite3.connect(DB_PATH)
    
    try:
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            return "No tables found in the database."

        output = []

        for table in tables:
            output.append(f"\nTABLE: {table}")

            # Get columns
            cursor.execute(f"PRAGMA table_info({table});")
            cols = cursor.fetchall()
            col_names = [col[1] for col in cols]
            output.append("Columns: " + ", ".join(col_names))

            # Sample rows
            try:
                sample_df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 3", conn)
                output.append("Sample rows:")
                output.append(sample_df.to_string(index=False))
            except Exception as e:
                output.append(f"Could not fetch sample rows: {str(e)}")

        return "\n".join(output)

    except Exception as e:
        return f"Schema error: {str(e)}"
    finally:
        conn.close()

#validate sql tool
@tool
def validate_sql(sql_query: str):
    """
    Use this tool to validate a SQL query before execution.
    This tool checks whether:
    - the query starts with SELECT
    - it does not contain dangerous commands such as DROP, DELETE, UPDATE, INSERT, ALTER, or CREATE
    Use this tool before running SQL.
    """
    print("Ollie is using validate_sql.")
    print(sql_query)

    query_upper = sql_query.strip().upper()

    if not query_upper.startswith("SELECT"):
        return "Invalid query: only SELECT statements are allowed."

    banned_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
    for keyword in banned_keywords:
        if keyword in query_upper:
            return f"Invalid query: contains forbidden keyword '{keyword}'."

    return "SQL query is valid."

#run sql tool
@tool
def run_sql(sql_query: str):
    """
    Use this tool to execute a validated SELECT SQL query on the Olist SQLite database.
    This tool should be used only after the SQL has been written and validated.
    It returns query results as a table-like string.
    Only SELECT queries are allowed.
    """
    print("Ollie is using run_sql.")
    print(sql_query)

    if not sql_query.strip().upper().startswith("SELECT"):
        return "Only SELECT queries are allowed."

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql_query, conn)
        return df.to_string(index=False)
    except Exception as e:
        return f"Query error: {str(e)}"
    finally:
        conn.close()