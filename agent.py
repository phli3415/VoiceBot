import os
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

llm = ChatOpenAI(
    model_name="gpt-4o-mini",  
    temperature=0.7,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)