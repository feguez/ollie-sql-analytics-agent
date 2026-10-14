# Imports
import base64
from pathlib import Path

import streamlit as st
from chatbot import initialize_messages, get_olist_response


# Ollie's logo and the questions used in both prompt locations
AGENT_ICON = Path(__file__).parent / "images" / "ollie_logo.png"
STARTER_PROMPTS = (
    "Which product categories generate the most revenue?",
    "What is the repeat purchase rate?",
    "How has order volume changed over time?",
    "What is the average delivery time for delivered orders?",
)
QUICK_LABELS = (
    "Revenue by category",
    "Repeat purchase rate",
    "Monthly order trends",
    "Delivery performance",
)

st.set_page_config(
    page_title="Ollie – AI SQL Analytics",
    page_icon=str(AGENT_ICON),
    layout="centered",
)


@st.cache_data
def logo_data_uri():
    return "data:image/png;base64," + base64.b64encode(AGENT_ICON.read_bytes()).decode()


logo_uri = logo_data_uri()
st.markdown(
    """
    <style>
    .stApp { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    /* Streamlit layout selectors keep the workspace narrow; check after upgrades. */
    /* Leave room for Streamlit's 60px toolbar above the product header. */
    [data-testid="stMainBlockContainer"] { max-width: 850px; padding-top: 5rem; }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: 1rem; }
    .ollie-brand { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.4rem; }
    .ollie-brand img { width: 48px; height: 48px; object-fit: contain; }
    .ollie-brand strong { font-size: 1.4rem; letter-spacing: -.03em; }
    .ollie-brand small { display: block; font-size: .75rem; color: #ABB3C9; margin-top: .15rem; }
    .ollie-dataset-label { color: #ABB3C9; font-size: .7rem; letter-spacing: .12em; margin-bottom: .5rem; }
    .ollie-dataset { color: #F3F4F6; font-size: .9rem; }
    .ollie-dataset-note { color: #ABB3C9; font-size: .75rem; margin-top: .35rem; }
    .ollie-hero { text-align: center; padding: 2rem 0 1.5rem; }
    .ollie-hero .ollie-intro { position: relative; width: 104px; margin: 0 auto; }
    .ollie-hero img { display: block; width: 104px; height: 104px; object-fit: contain;
        animation: ollie-idle 4s ease-in-out infinite; }
    .ollie-product { font-size: 1.3rem; font-weight: 650; letter-spacing: -.03em; margin-top: .4rem; }
    .ollie-hero .ollie-speech { position: absolute; left: calc(100% + .6rem); top: .4rem;
        display: grid; width: max-content; max-width: 330px; }
    /* Each message has 5.5 seconds of reading time and a .7-second crossfade. */
    .ollie-hero .ollie-bubble { position: relative; grid-area: 1 / 1; justify-self: start; align-self: center;
        width: max-content; max-width: 100%; padding: .55rem .8rem; text-align: left;
        border: 1px solid #E5DDF8; border-radius: 8px; background: #FFFFFF; color: #5B21B6;
        opacity: 0; pointer-events: none;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: .675rem; line-height: 1.2rem; font-weight: 400;
        animation: ollie-intro-fade 31s ease-in-out infinite; }
    /* Two triangles give the pointed tail a thin border and keep it clear of Ollie. */
    .ollie-hero .ollie-bubble::before, .ollie-hero .ollie-bubble::after { content: "";
        position: absolute; clip-path: polygon(0 80%, 100% 0, 100% 100%); }
    .ollie-hero .ollie-bubble::before { left: -28px; top: 13px; width: 28px; height: 10px;
        background: #E5DDF8; }
    .ollie-hero .ollie-bubble::after { left: -26px; top: 14px; width: 27px; height: 8px;
        background: #FFFFFF; clip-path: polygon(0 87.5%, 100% 0, 100% 100%); }
    .ollie-hero .ollie-bubble:first-child { opacity: 1; }
    .ollie-hero .ollie-bubble:nth-child(2) { animation-delay: -24.8s; }
    .ollie-hero .ollie-bubble:nth-child(3) { animation-delay: -18.6s; }
    .ollie-hero .ollie-bubble:nth-child(4) { animation-delay: -12.4s; }
    .ollie-hero .ollie-bubble:nth-child(5) { animation-delay: -6.2s; }
    @keyframes ollie-intro-fade {
        0%, 17.741935%, 100% { opacity: 1; }
        20%, 97.741935% { opacity: 0; }
    }
    @keyframes ollie-idle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    @media (prefers-reduced-motion: reduce) {
        .ollie-hero .ollie-bubble { animation: none; }
        .ollie-hero .ollie-bubble:not(:first-child) { visibility: hidden; }
        .ollie-hero img { animation: none; transform: none; }
    }
    .ollie-hero h1 { font-size: clamp(1.9rem, 5vw, 2.65rem); font-weight: 650;
        letter-spacing: -.045em; line-height: 1.2; padding: 1.25rem 0 .7rem; }
    .ollie-hero p { color: #6B7280; font-size: .95rem; line-height: 1.65;
        max-width: 540px; margin: 0 auto; }
    .ollie-compact { display: flex; align-items: center; gap: .5rem;
        border-bottom: 1px solid #E5E7EB; padding-bottom: 1rem; margin-bottom: .8rem; }
    /* Keep the image square without flex shrinking or inherited image limits. */
    .ollie-compact img { display: block; width: 28px; height: 28px; flex: 0 0 28px;
        max-width: none; max-height: none; object-fit: contain; margin: 0; padding: 0; }
    .ollie-compact strong { font-size: 1.05rem; }
    .st-key-starter_prompts button { min-height: 88px; text-align: left;
        justify-content: flex-start; padding: 1rem 1.15rem; background: #FFFFFF;
        border: 1px solid #E5E7EB; color: #374151; }
    .st-key-starter_prompts button:hover { border-color: #520DE2; background: #F5F2FF; color: #520DE2; }
    .st-key-starter_prompts button:focus-visible { outline: 2px solid #520DE2; outline-offset: 3px; }
    .st-key-quick_questions button { text-align: left; justify-content: flex-start; font-size: .85rem; }
    /* Native chat selectors provide small spacing and color adjustments. */
    [data-testid="stChatMessage"] { border-radius: 12px; padding: 1rem; }
    [data-testid="stChatMessageAvatarUser"] { background: #EDE9FE; color: #520DE2; }
    [data-testid="stChatInput"] { border: 1px solid #D9DCE5; }
    @media (max-width: 900px) {
        .ollie-hero .ollie-intro { display: flex; align-items: center; gap: .6rem;
            width: 100%; max-width: 320px; }
        .ollie-hero .ollie-intro img { flex: 0 0 104px; }
        .ollie-hero .ollie-speech { position: relative; left: auto; top: auto;
            width: auto; max-width: none; min-width: 0; flex: 1; grid-template-columns: minmax(0, 1fr); }
        .ollie-hero .ollie-bubble::before { left: -18px; width: 18px; top: calc(50% - 4px); }
        .ollie-hero .ollie-bubble::after { left: -16px; width: 17px; top: calc(50% - 3px); }
    }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding-top: 5rem; }
        .ollie-hero { padding-top: .5rem; }
        .ollie-hero img { width: 88px; height: 88px; }
        .ollie-hero .ollie-intro img { flex: 0 0 88px; }
        .ollie-hero .ollie-bubble::before { left: -16px; width: 16px; }
        .ollie-hero .ollie-bubble::after { left: -14px; width: 15px; }
        /* Streamlit column selectors let the starter cards stack on small screens. */
        .st-key-starter_prompts [data-testid="stHorizontalBlock"] { flex-direction: column; }
        .st-key-starter_prompts [data-testid="stColumn"] { width: 100% !important; flex: 1 1 auto !important; }
        .st-key-starter_prompts button { min-height: 68px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()
if "ollie_processing" not in st.session_state:
    st.session_state.ollie_processing = False
    st.session_state.ollie_prompt_ready = False

# Streamlit keeps old widgets until a run ends; hide the old cards while waiting
if st.session_state.ollie_processing:
    st.markdown(
        "<style>.st-key-starter_prompts, .ollie-hero { display: none; }</style>",
        unsafe_allow_html=True,
    )


def select_starter(prompt=None):
    # Ignore further clicks while a question is pending or being answered
    if st.session_state.ollie_processing:
        return
    if prompt is None:
        prompt = st.session_state.ollie_chat_input
    if prompt:
        st.session_state.ollie_starter_prompt = prompt
        st.session_state.ollie_processing = True
        st.session_state.ollie_prompt_ready = False


with st.sidebar:
    st.markdown(
        f'<div class="ollie-brand"><img src="{logo_uri}" alt="">'
        '<div><strong>Ollie</strong><small>AI SQL Analytics</small></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("New chat", use_container_width=True, disabled=st.session_state.ollie_processing):
        st.session_state.messages = initialize_messages()
        st.session_state.pop("ollie_starter_prompt", None)
        st.session_state.ollie_prompt_ready = False
        st.rerun()
    st.divider()
    st.markdown(
        '<div class="ollie-dataset-label">DATASET</div>'
        '<div class="ollie-dataset">Olist Brazilian E-Commerce</div>'
        '<div class="ollie-dataset-note">7 relational tables</div>',
        unsafe_allow_html=True,
    )


def compact_header():
    st.markdown(
        f'<div class="ollie-compact"><img src="{logo_uri}" alt="">'
        '<strong>Ollie</strong></div>',
        unsafe_allow_html=True,
    )


st.chat_input(
    "Ask Ollie a question...",
    key="ollie_chat_input",
    on_submit=select_starter,
    disabled=st.session_state.ollie_processing,
)
user_input = st.session_state.get("ollie_starter_prompt")
has_conversation = any(msg["role"] == "user" for msg in st.session_state.messages)

# Show sidebar questions only when the main starter cards are hidden
if has_conversation or user_input:
    with st.sidebar:
        st.divider()
        st.markdown('<div class="ollie-dataset-label">QUICK QUESTIONS</div>', unsafe_allow_html=True)
        with st.container(key="quick_questions"):
            for index, label in enumerate(QUICK_LABELS):
                st.button(
                    label,
                    key=f"quick_{index}",
                    use_container_width=True,
                    disabled=st.session_state.ollie_processing,
                    on_click=select_starter,
                    args=(STARTER_PROMPTS[index],),
                )

onboarding = st.empty()
if has_conversation or st.session_state.ollie_processing:
    # Remove the old hero and buttons before waiting for the response
    onboarding.empty()
with onboarding.container():
    if has_conversation or user_input:
        compact_header()
    else:
        st.markdown(
            f'<div class="ollie-hero"><div class="ollie-intro">'
            f'<img src="{logo_uri}" alt="Ollie logo">'
            '<div class="ollie-speech" role="note" '
            'aria-label="I can query the data for you. No SQL required. '
            'I turn questions into SQL. I’ll handle the query. I can explore the Olist data.">'
            '<span class="ollie-bubble" aria-hidden="true">I can query the data for you.</span>'
            '<span class="ollie-bubble" aria-hidden="true">No SQL required.</span>'
            '<span class="ollie-bubble" aria-hidden="true">I turn questions into SQL.</span>'
            '<span class="ollie-bubble" aria-hidden="true">I’ll handle the query.</span>'
            '<span class="ollie-bubble" aria-hidden="true">I can explore the Olist data.</span></div></div>'
            '<div class="ollie-product">Ollie</div>'
            '<h1>Ask your data, naturally.</h1>'
            '<p>Explore revenue, customers, products, reviews, and delivery performance '
            'across the Olist e-commerce dataset.</p></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="starter_prompts"):
            for row in range(2):
                columns = st.columns(2)
                for column_index, column in enumerate(columns):
                    prompt = STARTER_PROMPTS[row * 2 + column_index]
                    with column:
                        st.button(
                            prompt,
                            key=f"starter_{row}_{prompt}",
                            use_container_width=True,
                            disabled=st.session_state.ollie_processing,
                            on_click=select_starter,
                            args=(prompt,),
                        )

# Show chat history, skipping any system messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="👤").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant", avatar=str(AGENT_ICON)).write(msg["content"])

if user_input:
    # Finish the layout change in its own run before starting the backend call
    if not st.session_state.ollie_prompt_ready:
        st.session_state.ollie_prompt_ready = True
        st.rerun()
    user_input = st.session_state.pop("ollie_starter_prompt")
    # Display the question before waiting for Ollie's response
    st.chat_message("user", avatar="👤").write(user_input)
    try:
        with st.spinner("Ollie is thinking..."):
            response, updated_messages = get_olist_response(
                st.session_state.messages,
                user_input,
            )
        st.session_state.messages = updated_messages
        st.chat_message("assistant", avatar=str(AGENT_ICON)).write(response)
    finally:
        st.session_state.ollie_processing = False
        st.session_state.ollie_prompt_ready = False
    # Restore the controls and show the updated conversation
    st.rerun()
