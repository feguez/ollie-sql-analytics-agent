# Imports
# Streamlit to create the UI
# From chatbot.py import initialize messages to start convo memory
# Also get olist response, which sends the prompt to Ollie's backend logic
import streamlit as st
from chatbot import initialize_messages, get_olist_response

# Images
# Olist logo at the top, Ollie's icon in the chat messages
company_logo = "images/olist_logo.png"
agent_icon = "images/olist_agent_icon.png"

# Setting name in browser tab
# Centered layout to keep the interaction focused
st.set_page_config(
    page_title="Ollie – Analytics Assistant",
    layout="centered"
)

# Company logo and title
# Used simple HTML because the default title/subtitle are not centered by default
st.image(company_logo)
st.markdown(
    "<h1 style='text-align: center;'>Ollie – Analytics Assistant</h1>",
    unsafe_allow_html=True
)
# Subtitle
st.markdown(
    "<p style='text-align:center; color:#64748B;'>Ask questions about sales, payments, reviews, customers, and delivery performance at olist.</p>",
    unsafe_allow_html=True
)
# Ollie sidebar controls
# Start new chat button and disclaimer message
# Start new chat resets the convo memory calling initialize messages again, then rerunning the app.
# session state is what allows the app to remember the conversation
with st.sidebar:
    st.header("Ollie Controls")
    if st.button("Start New Chat"):
        st.session_state.messages = initialize_messages()
        st.rerun()
    st.markdown("---")
    st.caption("Ollie uses SQL tools and RAG documentation to answer Olist analytics questions.")
    st.markdown("---")

# You could try asking... in side bar
# Useful for a non-technical audience
with st.sidebar:
    st.header("You could try asking...")
    st.markdown("""
    - What are the top 5 payment types?
    - What is the correct way to calculate revenue?
    - What tables should I join for revenue by category?
    - Show me the schema of the database.
    """)

# Initialize conversation memory once per session
# The conversation is initialized with the system prompt
# session state is needed so chat history doesn't disappear after every prompt
# This block checks whether the conversation already exists, if not, it initializes one
if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()

# Show chat history and skip the system message
# Checks each message role and displays user messages w/ avatar and assistant messages w/ Ollie's icon
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="👤").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant", avatar=agent_icon).write(msg["content"])

# Chat input - input box at the bottom of the app
user_input = st.chat_input("Ask Ollie a question...")

# Sending prompt to Ollie
# App displays user prompt, then calls get_olist_response
# Key handoff from front end to backend
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
    # Once the backend returns Ollie's response and updated message history,
    # New memory is saved back into the session state
    st.session_state.messages = updated_messages

    # Display assistant (Ollie's) latest message
    st.chat_message("assistant", avatar=agent_icon).write(response)