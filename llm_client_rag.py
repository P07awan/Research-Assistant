from langchain_openai import ChatOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm_client_rag(api_key:str):
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.5
    )
    