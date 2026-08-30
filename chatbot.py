# Imports
# Bring everything Ollie needs on the backend
# dotenv (before using st.secrets and having pushed to streamlit) loads the API key
# LangChain creates the agent
# OpenAI embeddings are used for RAG
# FAISS loads the vector database
# Ollie_tools imports custom tools Ollie can call
import os
#from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings  # RAG: embeddings model
from langchain_community.vectorstores import FAISS   # RAG: vector store

from Ollie_tools import get_schema, validate_sql, run_sql

# Environment variables
# Loads .env file, where API key is stored (pre-push)
#load_dotenv()

# Now we directly use st.secrets from streamlit package
import streamlit as st
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
# gpt-4o-mini is enough for this project, taking care of credit usage
# init_chat_model lets the app connect to the specified LLM
# A temperature of 0.8 leans towards the deterministic side, but still keeps the conversational experience
MODEL_LLM = "openai:gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-ada-002"
MODEL = init_chat_model(MODEL_LLM, temperature=0.8)

# RAG: load FAISS index from disk
# The documents were split into chunks, embedded, and stored into faiss_index
# User asks a question -> Ollie searches vector store for context
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# System Prompt
# Defining Ollie's role, behavior, boundaries, tool usage rules
# Ollie should act like a business analytics assistant for the olist dataset, and rely on rools/retrieved context instead of making up numbers
# Important because the agent has tools but needs instruction on how to use them
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
- Ask a clarifying question only when missing information would materially change the meaning of the analysis.
- Do not ask for a time period, geography, or category when the user's question can reasonably be answered using the full available dataset.
- If a business term such as "best", "strongest", or "performing" could reasonably refer to multiple different metrics, ask the user which metric should define it before running SQL.
- Only use SELECT queries.
- Do not modify the database.

Core analytical rules:
- Revenue / GMV is calculated using SUM(order_items.price). Do not use payments.payment_value as revenue unless the user explicitly asks about payments.
- Total orders should use distinct order_id.
- Customer-level analysis should use customers.customer_unique_id when identifying the same customer across purchases.
- Repeat purchase rate must be measured at the persistent customer_unique_id level.
- The orders table does not contain customer_unique_id. Join orders o to customers c using o.customer_id = c.customer_id first.
- Then group by c.customer_unique_id and count DISTINCT o.order_id for each unique customer.
- A repeat customer is a customer_unique_id with more than one distinct order.
- Never group by customer_id to identify repeat customers; customer_id is not the persistent customer identifier for repeat-purchase analysis.- Only analyses specifically about delivery or logistics should default to delivered orders.
- When a metric requires counting entities that satisfy a grouped condition, do not treat the per-entity grouped rows as the final count. Aggregate the grouped result into a single summary row.
- For repeat purchase rate, first create a customer-level result grouped by customer_unique_id with each customer's distinct order count. Then calculate total customers and repeat customers from that customer-level result.
- Do not filter revenue, sales, order volume, customer, product, or geographic analyses by order_status unless the user explicitly requests a status filter or the metric definition requires one.
- In SQLite, timestamp fields are stored as text. When calculating elapsed time between timestamps, use SQLite date/time functions such as julianday() rather than directly subtracting timestamp strings.

How you respond:
- Be professional, structured, and concise.
- Use short sections or bullet points when helpful.
- State assumptions explicitly.
- When useful, explain which metric definition or business rule you followed.
- When writing formulas, use clean plain-text format instead of LaTeX.
- Example: Repeat Purchase Rate = (Customers with >1 order / Total Customers) × 100
- Do NOT use LaTeX formatting such as \frac or \text.
- When presenting monetary values, always include the appropriate currency.
- For the Olist dataset, use Brazilian Real (BRL) with the format: R$ value.
- Example: R$ 125.40

Identity consistency:
- Always speak as Ollie.
"""

# Create agent
# Combines the model, tools, system prompt into one object
# What allows Ollie to decide whether to answer directly, retrieve context, or call a tool
agent = create_agent(
    model=MODEL,
    tools=[get_schema, validate_sql, run_sql],
    system_prompt=SYSTEM_PROMPT
)

# Initialize conversation memory
# System prompt is already passed into create_agent, therefore this function returns an empty list, instead of starting w a system message
def initialize_messages():
    """
    Creates a new conversation with the system prompt.
    """
    return []

# Main response function - what app.py calls whenever the user submits a question
def get_olist_response(messages, user_input):
    """
    Takes the conversation history and user input,
    retrieves relevant RAG context,
    sends an augmented prompt to Ollie,
    and returns Ollie's response and updated messages.
    """

    # RAG: retrieve relevant chunks from FAISS and prepend them to the user prompt
    # Ollie searches FAISS index for 3 most relevant chunks to answer the users question
    # Chunks become extra context for the model
    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    # The Augmented part of Retrieval Augmented Generation
    # User question is combined with retrieved documentation BEFORE being sent to the agent
    augmented_prompt = f"""Use the following retrieved documentation context to help answer the user's question.
    Retrieved context:
    {context}
    User question:
    {user_input}
    """

    # Print the augmented prompt so we can see what RAG retrieved - Used for debugging
    print("\n--- AUGMENTED PROMPT ---")
    print(augmented_prompt)
    print("--- END AUGMENTED PROMPT ---\n")

    # Store original input (not the full augmented prompt) in memory for a clean chat history
    messages.append({"role": "user", "content": user_input})

    # Send augmented prompt to the agent for this turn
    # Replace the latest user message w the augmented version (includes RAG context)
    # The user sees a clear conversation, but the model recieves extra documentation
    agent_messages = messages[:-1] + [{"role": "user", "content": augmented_prompt}]
    results = agent.invoke({"messages": agent_messages})

    # Extract assistant response
    # Returns a list of messages after the agent finishes, the final message is Ollie's answer hence the [-1]
    assistant_message = results["messages"][-1].content

    # Updating memory
    # The assistant response is added to convo history and returned to app.py, to be displayed in the UI
    messages.append({"role": "assistant", "content": assistant_message})
    return assistant_message, messages