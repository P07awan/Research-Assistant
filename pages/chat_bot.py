# import neccessary libraries
import streamlit as st
import logging
from const import Constants
import requests
from config import settings

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session state Initilaization 
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "processed_file" not in st.session_state:
    st.session_state.processed_file = False

if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi 👋 Please upload the document. I’ll answer questions from it."}
        ]

# App configuration
st.set_page_config(layout= Constants.WIDE)


# Header and Description
st.header(Constants.HEADER_TITLE_CHAT_BOT)
st.markdown("---")
st.write(
    "Upload any research paper and instantly chat with it for clear, precise answers."
    "Discover related resources like YouTube, Semantic Scholar, and Wikipedia—all in one place ⚡ "
    "Turn your PDFs into an interactive learning companion 🚀"
)


# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF", type = Constants.PDF)

if uploaded_file is not None and st.session_state.processed_file is False:
    if st.session_state.api_key:
        st.toast("File uploaded successfully!")
        try:
            with st.spinner("Extracting the text ...."):
                
                backend_url = (settings.BACKEND_URL or "http://127.0.0.1:8000").rstrip("/")
                resp = requests.post(
                    f"{backend_url}/process_pdf",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    data={"api_key": st.session_state.api_key},
                    timeout=120
                )
                if resp.status_code == 200:
                    st.success("✅ PDF processed by backend")
                    st.session_state.processed_file = True
                else:
                    st.error(f"Backend error: {resp.json()['detail']}")
                
                st.session_state.processed_file = True  

        except Exception as e:
            st.session_state.processed_file = False
            st.error(f"Error processing the PDF: {str(e)}")
    else:
        st.error("API key not found")


# AI chat Functionalities (runs independently)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Please enter your prompt here...")

if user_input and st.session_state.api_key and uploaded_file is not None:
    
    with st.chat_message(Constants.USER):
        st.markdown(user_input)
        st.session_state.messages.append({"role": Constants.USER, "content": user_input})

    if not st.session_state.api_key:
        st.toast("❌ Enter your API key...", icon="⚠️")
    elif not st.session_state.processed_file:
        with st.chat_message(Constants.ASSISTANT):
            st.markdown("📄 Please upload a PDF first.")
        st.session_state.messages.append({"role": Constants.ASSISTANT, "content": "📄 Please upload a PDF first."})
    
    else:
        try:
            with st.spinner("Thinking..."):

                backend_url = (settings.BACKEND_URL or "http://127.0.0.1:8000").rstrip("/")
                response = requests.post(
                    f"{backend_url}/query",
                    json={"query": user_input},
                    timeout=120
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]

                    with st.chat_message(Constants.ASSISTANT):
                        st.markdown(answer)
                    st.session_state.messages.append({"role": Constants.ASSISTANT, "content": answer})

                else:
                    st.error(f"Backend error: {response.json()['detail']}")

        except Exception as e:
            st.error(f"Error during response generation: {str(e)}")
