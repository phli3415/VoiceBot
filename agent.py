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

def create_patient_agent(scenario: dict) -> ConversationChain:
    template = f"""
        You are an automated voice bot acting as a patient to test an AI medical assistant.
        Your goal is to realistically play the part of the patient based on the scenario below.
        Keep your responses concise and natural, as if you were speaking on the phone.
        Do not reveal that you are a bot.

        Current Scenario: {scenario['description']}

        Current conversation:
        {{history}}
        AI Assistant: {{input}}
        Patient:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

    agent = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        verbose=True,
        memory=ConversationBufferMemory(ai_prefix="AI Assistant", human_prefix="Patient")
    )

    agent.memory.chat_memory.add_user_message(scenario['initial_prompt'])

    return agent



def analyze_conversation(conversation_history: str, scenario: dict) -> str:
    
    analyzer_llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

    analysis_prompt = f"""
    As a quality assurance expert, your task is to analyze the following conversation between a patient bot and an AI medical assistant. Your analysis should be ruthless and detailed.

    **Test Scenario:**
    - Description: {scenario['description']}
    - Expected Outcome: {scenario['expected_outcome']}

    **Full Conversation Transcript:**
    --- START --- 
    {conversation_history}
    --- END ---

    **Analysis Checklist:**
    1.  **Correctness**: Did the AI assistant provide accurate information? Did it correctly understand the patient's requests?
    2.  **Task Completion**: Was the AI assistant able to fulfill the patient's goal as described in the scenario?
    3.  **Hallucinations**: Did the AI make up any information, features, or procedures?
    4.  **Failures to Understand**: Were there moments where the AI clearly misunderstood the patient? Document them.
    5.  **Awkward Phrasing**: Was the AI's language natural and conversational, or was it robotic and awkward?
    6.  **Overall Quality**: Provide a summary of the AI's performance and a rating from 1 (terrible) to 5 (perfect).

    Produce a concise report based on the checklist.
    """

    response = analyzer_llm.predict(text=analysis_prompt)
    return response
