import html
import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Local Knowledge Chat",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    max-width: 900px;
    padding-top: 3.5rem;
    padding-bottom: 5rem;
}

header, footer, #MainMenu {
    visibility: hidden;
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.title {
    font-size: 2.2rem;
    font-weight: 650;
    letter-spacing: -0.04em;
    text-align: center;
    color: #111;
    margin-bottom: 0.4rem;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}

.upload-title {
    font-size: 0.95rem;
    font-weight: 500;
    color: #111;
    margin-bottom: 0.25rem;
}

.upload-caption {
    font-size: 0.86rem;
    color: #777;
    margin-bottom: 1rem;
}

.document-list {
    font-size: 0.86rem;
    color: #333;
    margin-top: 0.75rem;
    margin-bottom: 2rem;
}

.document-item {
    padding: 0.25rem 0;
    color: #444;
}

.chat-block {
    margin-bottom: 1.6rem;
}

.chat-label {
    font-size: 0.78rem;
    color: #777;
    margin-bottom: 0.35rem;
}

.chat-content {
    font-size: 0.98rem;
    line-height: 1.65;
    color: #111;
}

.user-message {
    background: #f7f7f7;
    border-radius: 12px;
    padding: 0.75rem 1rem;
}

.assistant-message {
    padding: 0.25rem 0;
}

[data-testid="stFileUploader"] section {
    border: 1px solid #ddd;
    background: #fff;
}

[data-testid="stFileUploader"] button {
    border-radius: 999px;
    border: 1px solid #111;
    background: #fff;
    color: #111;
}

[data-testid="stChatInput"] {
    max-width: 760px;
    margin: 0 auto;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f7f7f8;
    border-right: 1px solid #e5e5e5;
}

[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border: none !important;
    background: transparent !important;
    color: #111 !important;
    border-radius: 8px !important;
    padding: 0.45rem 0.65rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    min-height: 2rem !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #ececec !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 8px;
    padding: 0.45rem 0.65rem;
    margin-bottom: 0.15rem;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #ececec;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    font-size: 0.9rem;
    color: #111;
}

[data-testid="stSidebar"] hr {
    margin: 1rem 0;
}

.sidebar-label {
    font-size: 0.78rem;
    color: #777;
    margin: 1rem 0 0.4rem 0.25rem;
}

.sidebar-small {
    font-size: 0.78rem;
    color: #777;
    margin-bottom: 0.35rem;
}
</style>
""", unsafe_allow_html=True)


def upload_document(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type,
        )
    }

    response = requests.post(
        f"{BACKEND_URL}/documents/upload",
        files=files,
        timeout=180,
    )

    if not response.ok:
        raise RuntimeError(response.text)


def clear_documents():
    response = requests.delete(
        f"{BACKEND_URL}/documents/clear",
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(response.text)


def ask_question(question: str):
    response = requests.post(
        f"{BACKEND_URL}/chat/",
        json={"question": question},
        timeout=240,
    )

    if not response.ok:
        raise RuntimeError(response.text)

    return response.json()


def new_chat():
    chat_number = len(st.session_state.chats) + 1
    chat_name = f"Chat {chat_number}"

    st.session_state.chats[chat_name] = []
    st.session_state.active_chat = chat_name


def rename_chat(old_name: str, new_name: str):
    new_name = new_name.strip()

    if not new_name or new_name == old_name:
        return

    if new_name in st.session_state.chats:
        return

    st.session_state.chats[new_name] = st.session_state.chats.pop(old_name)

    if st.session_state.active_chat == old_name:
        st.session_state.active_chat = new_name


def delete_chat(chat_name: str):
    if len(st.session_state.chats) == 1:
        st.session_state.chats = {"Chat 1": []}
        st.session_state.active_chat = "Chat 1"
        return

    st.session_state.chats.pop(chat_name, None)

    if st.session_state.active_chat == chat_name:
        st.session_state.active_chat = next(iter(st.session_state.chats))


def render_message(role, content):
    label = "You" if role == "user" else "Assistant"
    message_class = "user-message" if role == "user" else "assistant-message"
    safe_content = html.escape(content).replace("\n", "<br>")

    st.markdown(
        f"""
<div class="chat-block">
    <div class="chat-label">{label}</div>
    <div class="chat-content {message_class}">
        {safe_content}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


with st.sidebar:
    if st.button("New chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown('<div class="sidebar-label">Chats</div>', unsafe_allow_html=True)

    chat_names = list(st.session_state.chats.keys())

    selected_chat = st.radio(
        "Chats",
        chat_names,
        index=chat_names.index(st.session_state.active_chat),
        label_visibility="collapsed",
    )

    st.session_state.active_chat = selected_chat

    st.markdown("---")

    st.markdown('<div class="sidebar-small">Rename selected chat</div>', unsafe_allow_html=True)

    new_name = st.text_input(
        "Rename selected chat",
        value=st.session_state.active_chat,
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Rename", use_container_width=True):
            rename_chat(st.session_state.active_chat, new_name)
            st.rerun()

    with col2:
        if st.button("Delete", use_container_width=True):
            delete_chat(st.session_state.active_chat)
            st.rerun()

    st.markdown("---")

    if st.button("Clear documents", use_container_width=True):
        try:
            clear_documents()
            st.session_state.uploaded_files = []
            st.session_state.chats = {"Chat 1": []}
            st.session_state.active_chat = "Chat 1"
            st.rerun()
        except Exception as exc:
            st.error("Could not clear documents.")
            st.caption(str(exc))


st.markdown('<div class="title">Local Knowledge Chat</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ask questions grounded only in your uploaded documents.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="upload-title">Upload documents</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="upload-caption">Drop one or more PDF, TXT, or Markdown files.</div>',
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Upload documents",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.uploaded_files:
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                try:
                    upload_document(uploaded_file)
                    st.session_state.uploaded_files.append(uploaded_file.name)
                except Exception as exc:
                    st.error(f"Could not upload {uploaded_file.name}")
                    st.caption(str(exc))


if st.session_state.uploaded_files:
    st.markdown('<div class="document-list">', unsafe_allow_html=True)

    for file_name in st.session_state.uploaded_files:
        st.markdown(
            f'<div class="document-item">{html.escape(file_name)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


active_messages = st.session_state.chats[st.session_state.active_chat]

for message in active_messages:
    render_message(
        message["role"],
        message["content"],
    )


question = st.chat_input("Ask about your documents...")

if question:
    active_messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    render_message("user", question)

    with st.spinner("Searching documents and generating grounded response..."):
        try:
            data = ask_question(question)

            answer = data.get("answer", "").strip()

            if not answer:
                answer = "I could not find this in the uploaded documents."

            render_message("assistant", answer)

            active_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as exc:
            error_message = "I could not complete the request."

            st.error(error_message)
            st.caption(str(exc))

            active_messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )