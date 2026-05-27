# Ollie SQL Analytics Agent

Ollie is an AI-powered SQL analytics agent that translates natural language business questions into SQL queries, retrieves insights from a database, and uses RAG documentation to ground responses in business context.

The project was built for **BSAN 400: GenAI for Business Insight** and demonstrates how AI agents can support business analytics workflows by combining a conversational interface, database tools, and retrieval-augmented generation.

---

## Project Overview

Business users often need answers from data but may not know SQL or may not know which tables, joins, or metric definitions to use. Ollie helps bridge that gap by allowing users to ask questions in plain English and receive data-backed answers with business-friendly explanations.

Ollie is built around the **Olist Brazilian E-Commerce dataset**, which includes information about orders, customers, products, sellers, payments, reviews, and delivery performance.

---

## Key Features

- **Natural language analytics interface**  
  Users can ask business questions without writing SQL.

- **SQL query generation and execution**  
  Ollie can generate SQL queries, validate them, and run them against a SQLite database.

- **Tool-based agent architecture**  
  Ollie uses LangChain tools to inspect the database schema, validate SQL, and execute queries safely.

- **RAG-grounded responses**  
  Ollie uses project documentation such as a data dictionary, business rules, and SQL safety guidelines to provide more reliable answers.

- **Streamlit user interface**  
  A clean web app interface allows users to interact with Ollie through a simple chat experience.

---

## Example Questions

Users can ask Ollie questions such as:

- What is the correct way to calculate total revenue?
- What are the top 5 payment types in the Olist database?
- What tables should I join to calculate revenue by product category?
- Which product categories drive the most revenue?
- How should SQL queries be written safely in this project?

---

## Tech Stack

- Python
- Streamlit
- OpenAI API
- LangChain
- FAISS
- SQLite
- Pandas

---

## Project Architecture

```text
User
 ↓
Streamlit App
 ↓
Ollie Agent Logic
 ↓
RAG Context Retrieval + SQL Tools
 ↓
SQLite Database / FAISS Vector Store
 ↓
Business-Friendly Answer
