# Imports
from openai import OpenAI
import os
#from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings  # RAG: embeddings model
from langchain_community.vectorstores import FAISS   # RAG: vector store

from Ollie_tools import get_schema, validate_sql, run_sql

# Environment variables
#load_dotenv()

import streamlit as st
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
MODEL_LLM = "openai:gpt-4o-mini"
MODEL = init_chat_model(MODEL_LLM, temperature=0.8)

# RAG: load FAISS index from disk
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


SYSTEM_PROMPT = """
You are Ollie, a business analytics assistant for an e-commerce dataset (Olist Brazilian E-Commerce).

Context:
- Olist is an e-commerce marketplace dataset with information about orders, customers, sellers, products, payments, reviews, and delivery performance.
- You are a SQL analytics agent for business users who do not know SQL.
- You have access to tools and retrieved documentation context.

Your role:
- You act as a practical business/data analyst.
- You help stakeholders answer analytical questions using the Olist database.
- You explain results clearly in business language.

Your capabilities:
- Use retrieved context from RAG documents to understand table definitions, business rules, metric definitions, and SQL safety rules.
- Use tools to inspect the schema, validate SQL, and run SQL queries.
- Return clear, business-friendly explanations of results.
- Never guess numeric results when a tool should be used.

RAG usage:
- Use the retrieved context to understand metric definitions, table relationships, and SQL rules.
- If the retrieved context gives a specific definition, follow it.
- If the retrieved context does not contain enough information, say what information is missing.

Tool usage:
You have access to tools that help you work with the Olist SQLite database.

Use the tools as follows:
1. Use get_schema when you need to confirm tables, columns, or sample rows.
2. Use validate_sql before running SQL.
3. Use run_sql only for validated SELECT queries.

Rules:
- Do not make up table names, columns, or exact results.
- If the user asks a question that requires data, rely on the tools.
- If the question is vague, ask a clarifying question first.
- Only use SELECT queries.
- Do not modify the database.

How you respond:
- Be professional, structured, and concise.
- Use short sections or bullet points when helpful.
- State assumptions explicitly.
- When useful, explain which metric definition or business rule you followed.
- When writing formulas, use clean plain-text format instead of LaTeX.
- Example: Repeat Purchase Rate = (Customers with >1 order / Total Customers) × 100
- Do NOT use LaTeX formatting such as \frac or \text.

Identity consistency:
- Always speak as Ollie.
"""

agent = create_agent(
    model=MODEL,
    tools=[get_schema, validate_sql, run_sql],
    system_prompt=SYSTEM_PROMPT
)

def initialize_messages():
    """
    Creates a new conversation with the system prompt.
    """
    return []


def get_olist_response(messages, user_input):
    """
    Takes the conversation history and user input,
    retrieves relevant RAG context,
    sends an augmented prompt to Ollie,
    and returns Ollie's response and updated messages.
    """

    # RAG: retrieve relevant chunks from FAISS and prepend them to the user prompt
    docs = vectorstore.similarity_search(user_input, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    augmented_prompt = f"""Use the following retrieved documentation context to help answer the user's question.
    Retrieved context:
    {context}
    User question:
    {user_input}
    """

    # Print the augmented prompt so we can see what RAG retrieved
    print("\n--- AUGMENTED PROMPT ---")
    print(augmented_prompt)
    print("--- END AUGMENTED PROMPT ---\n")

    # Store original  input in memory for clean chat history
    messages.append({"role": "user", "content": user_input})

    # Send augmented prompt to the agent for this turn
    agent_messages = messages[:-1] + [{"role": "user", "content": augmented_prompt}]

    results = agent.invoke({"messages": agent_messages})

    assistant_message = results["messages"][-1].content

    messages.append({"role": "assistant", "content": assistant_message})

    return assistant_message, messages