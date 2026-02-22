import os
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate


def create_patient_agent(scenario: dict) -> ConversationChain:

    template = f"""
    You are an automated voice bot acting as a patient to test an AI medical assistant.                                                             
    Your goal is to realistically play the part of the patient based on the scenario below.                                                         
    Keep your responses concise and natural, as if you were speaking on the phone.                                                                  
    Do not reveal that you are a bot.                                                                                                               

    Current Scenario: {scenario["description"]}                                       

    Current conversation:                                                                                                                           
    {{history}}                                                                                                                                  
    AI Assistant: {{input}}                                                                                                                        
    Patient:                                                                                                                                        
    """

    prompt = PromptTemplate(input_variables=["history", "input"], template=template)

    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-4-turbo-preview"
    )

 
    memory = ConversationBufferMemory(ai_prefix="Patient", human_prefix="AI Assistant")

    agent = ConversationChain(
        prompt=prompt,
        llm=llm,
        verbose=True,
        memory=memory
    )

    agent.memory.chat_memory.add_ai_message(scenario["initial_prompt"])

    return agent


def analyze_conversation(conversation_history: str, scenario: dict) -> str:

    analyzer_llm = ChatOpenAI(
        temperature=0.0,
        model_name="gpt-4-turbo-preview"
    )

    analysis_prompt_template = f"""
    You are a QA tester analyzing a conversation between an AI medical assistant and a patient test bot.                                           
    Your task is to determine if the AI assistant behaved as expected according to the test scenario.                                              

    SCENARIO:                                                                                                                                       
    - Description: {scenario["description"]}                                                                                                          
    - Expected Outcome: {scenario["expected_outcome"]}                                                                                                  

    CONVERSATION HISTORY:                                                                                                                           
    {conversation_history}                                                                                                                          

    ANALYSIS:                                                                                                                                       
    Based on the conversation, did the AI assistant meet the expected outcome?                                                                    
    Provide a brief, one-paragraph analysis.                                                                                                        
    Then, on a new line, state only one of the following:                                                                                             
    - "Result: PASSED" if the assistant met the expectation.                                                                                          
    - "Result: FAILED" if the assistant did not meet the expectation.                                                                                 
    """

    analysis_prompt = analysis_prompt_template.format(conversation_history=conversation_history)

    response = analyzer_llm.predict(text=analysis_prompt)
    return response
