import streamlit as st
from chatbot import initialize_messages, get_olist_response

# Images
company_logo = "images/olist_logo.png"
agent_icon = "images/olist_agent_icon.png"

# Setting name in browser tab
st.set_page_config(
    page_title="Ollie – Analytics Assistant",
    layout="centered"
)

# Company logo and title
st.image(company_logo)
st.markdown(
    "<h1 style='text-align: center;'>Ollie – Analytics Assistant</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; color:#64748B;'>Ask questions about sales, payments, reviews, customers, and delivery performance at olist.</p>",
    unsafe_allow_html=True
)

# Ollie controls (start new chat button and disclaimer message) in side bar
with st.sidebar:
    st.header("Ollie Controls")
    if st.button("Start New Chat"):
        st.session_state.messages = initialize_messages()
        st.rerun()
    st.markdown("---")
    st.caption("Ollie uses SQL tools and RAG documentation to answer Olist analytics questions.")
    st.markdown("---")

# You could try asking... in side bar
with st.sidebar:
    st.header("You could try asking...")
    st.markdown("""
    - What are the top 5 payment types?
    - What is the correct way to calculate revenue?
    - What tables should I join for revenue by category?
    - Show me the schema of the database.
    """)

# Initialize conversation memory once per session - The conversation is initialized with the system prompt
if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()

# Show chat history and skip the system message
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="👤").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant", avatar=agent_icon).write(msg["content"])

# Chat input
user_input = st.chat_input("Ask Ollie a question...")

if user_input:
    # Display user message
    st.chat_message("user", avatar="👤").write(user_input)

    # Get agent response
    with st.spinner("Ollie is thinking..."):
        response, updated_messages = get_olist_response(
            st.session_state.messages,
            user_input
        )

    # Update memory
    st.session_state.messages = updated_messages

    # Display assistant message
    st.chat_message("assistant", avatar=agent_icon).write(response)